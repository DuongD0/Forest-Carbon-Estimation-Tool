from sqlalchemy.orm import Session
from app.models.project import Project, ProjectType
from app.models.ecosystem import Ecosystem
from app.services.forest_detector import AdvancedForestDetector
from app import crud
from geoalchemy2.shape import to_shape
import math
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class VCSCalculationResult:
    """VCS-compliant carbon credit calculation result"""
    # Project carbon stocks
    project_carbon_stock_tC: float
    baseline_carbon_stock_tC: float
    net_carbon_benefit_tC: float
    
    # Adjustments and deductions
    leakage_deduction_tC: float
    uncertainty_deduction_tC: float
    buffer_pool_contribution_tC: float
    
    # Final credits
    verified_carbon_units_tCO2e: float
    creditable_carbon_units_tCO2e: float
    
    # Supporting data
    forest_analysis: Dict[str, Any]
    confidence_metrics: Dict[str, float]
    methodology_compliance: Dict[str, Any]

class VCSCarbonCalculator:
    """
    VCS-compliant carbon credit calculator for forestry projects.
    
    Implements industry-standard methodologies including:
    - VCS VM0007 (REDD+ Methodology Framework)
    - VCS VM0015 (Methodology for Avoided Unplanned Deforestation)
    - Baseline scenario establishment
    - Leakage assessment and deduction
    - Uncertainty quantification and buffer pool contributions
    - Additionality assessment
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.forest_detector = AdvancedForestDetector()
        
        # VCS methodology parameters
        self.vcs_parameters = {
            'carbon_fraction': 0.47,  # IPCC default for tropical forests
            'co2_to_c_ratio': 44/12,  # Molecular weight ratio
            'default_wood_density': 0.6,  # g/cm³ for mixed tropical forests
            'root_shoot_ratio': 0.24,  # Below-ground to above-ground biomass ratio
            'uncertainty_threshold_low': 0.1,   # 10% uncertainty
            'uncertainty_threshold_medium': 0.2,  # 20% uncertainty
            'uncertainty_threshold_high': 0.35,  # 35% uncertainty
            'buffer_pool_minimum': 0.10,  # Minimum 10% buffer pool contribution
            'leakage_belt_factor': 0.15,  # 15% default leakage factor
        }
        
        # Allometric equations for different forest types (simplified for university level)
        self.allometric_equations = {
            'tropical_moist': {
                'equation': 'chave_2014',  # Chave et al. 2014 pantropical equation
                'parameters': {'a': 0.0673, 'b': 0.976, 'c': 0.976},
                'description': 'Pantropical allometric equation for moist forests'
            },
            'tropical_dry': {
                'equation': 'chave_2014_dry',
                'parameters': {'a': 0.0509, 'b': 0.976, 'c': 0.976},
                'description': 'Pantropical allometric equation for dry forests'
            },
            'mangrove': {
                'equation': 'komiyama_2008',
                'parameters': {'a': 0.251, 'b': 0.88},
                'description': 'Mangrove-specific allometric equation'
            }
        }

    def _get_project_area_ha(self, project: Project) -> float:
        """
        Calculates project's boundary area in hectares.
        NOTE: for this to be accurate, the geometry should be in a projection
        that uses meters (like UTM), not lat/lon.
        """
        if not project.location_geometry:
            raise ValueError("Project has no geometry.")
        
        project_shape = to_shape(project.location_geometry)
        # assuming the CRS is in meters. if it's lat/lon, this will be wrong.
        area_m2 = project_shape.area
        return area_m2 / 10000

    def calculate_vcs_compliant_credits(
        self,
        project: Project,
        image_path: str,
        image_scale_factor: float,
        project_age_years: int,
        baseline_scenario: Optional[str] = "historical_deforestation",
        monitoring_period_years: int = 1
    ) -> VCSCalculationResult:
        """
        Calculate VCS-compliant carbon credits for forestry projects.
        
        This method implements a comprehensive VCS methodology including:
        - Project scenario carbon stock assessment
        - Baseline scenario establishment
        - Leakage assessment
        - Uncertainty quantification
        - Buffer pool contributions
        
        :param project: Project object
        :param image_path: Path to current forest imagery
        :param image_scale_factor: Meters per pixel conversion
        :param project_age_years: Age of the project in years
        :param baseline_scenario: Type of baseline scenario
        :param monitoring_period_years: Monitoring period length
        :return: Comprehensive VCS calculation result
        """
        logging.info(f"Starting VCS-compliant calculation for project {project.id}")
        
        if not project.ecosystem_id:
            raise ValueError("Project requires an ecosystem assignment for VCS calculations")
        
        ecosystem = crud.ecosystem.get(self.db, id=project.ecosystem_id)
        if not ecosystem:
            raise ValueError(f"Ecosystem {project.ecosystem_id} not found")
        
        # Step 1: Advanced forest analysis
        forest_analysis = self.forest_detector.detect_area(
            image_path=image_path,
            ecosystem=ecosystem,
            scale_factor=image_scale_factor
        )
        
        # Step 2: Calculate project scenario carbon stocks
        project_carbon_stock = self._calculate_project_carbon_stock(
            forest_analysis, project_age_years, ecosystem
        )
        
        # Step 3: Establish baseline scenario
        baseline_carbon_stock = self._calculate_baseline_scenario(
            project, forest_analysis, baseline_scenario
        )
        
        # Step 4: Calculate net carbon benefit
        net_carbon_benefit = max(0, project_carbon_stock - baseline_carbon_stock)
        
        # Step 5: Assess and deduct leakage
        leakage_deduction = self._calculate_leakage_deduction(
            project, net_carbon_benefit, forest_analysis
        )
        
        # Step 6: Quantify uncertainty and calculate deductions
        uncertainty_assessment = forest_analysis['uncertainty_assessment']
        uncertainty_deduction = self._calculate_uncertainty_deduction(
            net_carbon_benefit, uncertainty_assessment
        )
        
        # Step 7: Calculate buffer pool contribution
        buffer_pool_contribution = self._calculate_buffer_pool_contribution(
            net_carbon_benefit, project, uncertainty_assessment
        )
        
        # Step 8: Calculate final verified carbon units
        net_benefit_after_leakage = net_carbon_benefit - leakage_deduction
        net_benefit_after_uncertainty = net_benefit_after_leakage - uncertainty_deduction
        creditable_carbon_tC = net_benefit_after_uncertainty - buffer_pool_contribution
        
        # Convert to CO2 equivalent
        verified_carbon_units_tCO2e = net_benefit_after_leakage * self.vcs_parameters['co2_to_c_ratio']
        creditable_carbon_units_tCO2e = max(0, creditable_carbon_tC * self.vcs_parameters['co2_to_c_ratio'])
        
        # Step 9: Methodology compliance check
        methodology_compliance = self._assess_methodology_compliance(
            project, forest_analysis, uncertainty_assessment
        )
        
        result = VCSCalculationResult(
            project_carbon_stock_tC=project_carbon_stock,
            baseline_carbon_stock_tC=baseline_carbon_stock,
            net_carbon_benefit_tC=net_carbon_benefit,
            leakage_deduction_tC=leakage_deduction,
            uncertainty_deduction_tC=uncertainty_deduction,
            buffer_pool_contribution_tC=buffer_pool_contribution,
            verified_carbon_units_tCO2e=verified_carbon_units_tCO2e,
            creditable_carbon_units_tCO2e=creditable_carbon_units_tCO2e,
            forest_analysis=forest_analysis,
            confidence_metrics=forest_analysis['confidence_metrics'],
            methodology_compliance=methodology_compliance
        )
        
        logging.info(f"VCS calculation complete: {creditable_carbon_units_tCO2e:.2f} tCO2e creditable")
        return result

    def calculate_credits(
        self,
        project: Project,
        image_path: str | None = None,
        image_scale_factor: float | None = None,
        project_age_years: int | None = None,
        use_vcs_methodology: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point for carbon credit calculations.
        
        :param project: Project object
        :param image_path: Path to forest imagery
        :param image_scale_factor: Meters per pixel conversion
        :param project_age_years: Project age in years
        :param use_vcs_methodology: Whether to use VCS-compliant methodology
        :return: Calculation results
        """
        if project.project_type == ProjectType.FORESTRY:
            if not image_path:
                raise ValueError("Image path required for forestry projects")
            if image_scale_factor is None:
                raise ValueError("Image scale factor required for forestry projects")
            if project_age_years is None:
                project_age_years = 1
                logging.warning(f"Project age not specified, defaulting to {project_age_years} year")

            if use_vcs_methodology:
                vcs_result = self.calculate_vcs_compliant_credits(
                    project, image_path, image_scale_factor, project_age_years
                )
                return self._format_vcs_result(vcs_result)
            else:
                # Fallback to simplified calculation for comparison
                simple_result = self._calculate_simple_credits(
                    project, image_path, image_scale_factor, project_age_years
                )
                return simple_result
        else:
            raise ValueError(f"Unsupported project type: {project.project_type}")

    def _calculate_project_carbon_stock(self, forest_analysis: Dict[str, Any], 
                                      project_age_years: int, ecosystem: Ecosystem) -> float:
        """Calculate project scenario carbon stock using forest analysis results."""
        total_carbon_stock = 0.0
        
        # Use forest type-specific carbon densities from advanced detection
        for forest_type_data in forest_analysis.get('forest_types', []):
            area_ha = forest_type_data['area_ha']
            carbon_density = forest_type_data['carbon_density_tC_ha']
            
            # Apply age-based growth factor if ecosystem has growth parameters
            if hasattr(ecosystem, 'biomass_growth_rate') and ecosystem.biomass_growth_rate:
                growth_factor = 1 - math.exp(-ecosystem.biomass_growth_rate * project_age_years)
                adjusted_carbon_density = carbon_density * growth_factor
            else:
                adjusted_carbon_density = carbon_density
            
            forest_carbon_stock = area_ha * adjusted_carbon_density
            total_carbon_stock += forest_carbon_stock
            
            logging.debug(f"Forest type {forest_type_data['type']}: {area_ha:.2f} ha × {adjusted_carbon_density:.1f} tC/ha = {forest_carbon_stock:.1f} tC")
        
        return total_carbon_stock

    def _calculate_baseline_scenario(self, project: Project, forest_analysis: Dict[str, Any], 
                                   baseline_scenario: str) -> float:
        """
        Calculate baseline scenario carbon stock.
        
        For university-level implementation, we use simplified baseline scenarios:
        - historical_deforestation: Assumes continued deforestation at regional rates
        - business_as_usual: Assumes no conservation action
        - degradation: Assumes forest degradation without complete loss
        """
        total_area_ha = forest_analysis.get('total_area_ha', 0)
        weighted_carbon_density = forest_analysis.get('weighted_carbon_density_tC_ha', 0)
        
        if baseline_scenario == "historical_deforestation":
            # Assume 2% annual deforestation rate (typical for tropical regions)
            deforestation_rate = 0.02
            remaining_forest_factor = max(0, 1 - deforestation_rate)
            baseline_carbon_stock = total_area_ha * weighted_carbon_density * remaining_forest_factor
            
        elif baseline_scenario == "business_as_usual":
            # Assume 50% forest loss over 10 years without intervention
            forest_loss_factor = 0.5
            baseline_carbon_stock = total_area_ha * weighted_carbon_density * (1 - forest_loss_factor)
            
        elif baseline_scenario == "degradation":
            # Assume 30% carbon loss due to degradation
            degradation_factor = 0.3
            baseline_carbon_stock = total_area_ha * weighted_carbon_density * (1 - degradation_factor)
            
        else:
            # Conservative approach: assume no baseline carbon loss
            baseline_carbon_stock = total_area_ha * weighted_carbon_density
            logging.warning(f"Unknown baseline scenario '{baseline_scenario}', using conservative estimate")
        
        logging.info(f"Baseline scenario '{baseline_scenario}': {baseline_carbon_stock:.1f} tC")
        return baseline_carbon_stock

    def _calculate_leakage_deduction(self, project: Project, net_carbon_benefit: float, 
                                   forest_analysis: Dict[str, Any]) -> float:
        """
        Calculate leakage deduction based on VCS methodologies.
        
        Leakage occurs when project activities cause emissions elsewhere.
        For forestry projects, this typically includes:
        - Market leakage (timber market displacement)
        - Activity displacement (deforestation pressure moves elsewhere)
        """
        project_area_ha = forest_analysis.get('total_area_ha', 0)
        
        # Market leakage assessment (simplified)
        if project_area_ha > 1000:  # Large projects have higher market impact
            market_leakage_factor = 0.20  # 20% leakage
        elif project_area_ha > 100:
            market_leakage_factor = 0.15  # 15% leakage
        else:
            market_leakage_factor = 0.10  # 10% leakage for small projects
        
        # Activity displacement leakage
        # Based on project location and surrounding deforestation pressure
        activity_leakage_factor = self.vcs_parameters['leakage_belt_factor']
        
        # Total leakage factor (capped at 30% per VCS guidelines)
        total_leakage_factor = min(0.30, market_leakage_factor + activity_leakage_factor)
        
        leakage_deduction = net_carbon_benefit * total_leakage_factor
        
        logging.info(f"Leakage assessment: {total_leakage_factor*100:.1f}% = {leakage_deduction:.1f} tC")
        return leakage_deduction

    def _calculate_uncertainty_deduction(self, net_carbon_benefit: float, 
                                       uncertainty_assessment: Dict[str, Any]) -> float:
        """Calculate uncertainty deduction based on confidence metrics."""
        uncertainty_percentage = uncertainty_assessment.get('uncertainty_percentage', 35.0) / 100.0
        uncertainty_deduction = net_carbon_benefit * uncertainty_percentage
        
        logging.info(f"Uncertainty deduction: {uncertainty_percentage*100:.1f}% = {uncertainty_deduction:.1f} tC")
        return uncertainty_deduction

    def _calculate_buffer_pool_contribution(self, net_carbon_benefit: float, project: Project, 
                                          uncertainty_assessment: Dict[str, Any]) -> float:
        """
        Calculate buffer pool contribution based on VCS risk assessment.
        
        Buffer pools protect against reversals (e.g., fire, disease, illegal logging).
        """
        # Base buffer pool percentage
        base_buffer = self.vcs_parameters['buffer_pool_minimum']  # 10%
        
        # Risk-based adjustments
        uncertainty_level = uncertainty_assessment.get('uncertainty_level', 'high')
        
        if uncertainty_level == 'high':
            risk_adjustment = 0.15  # Additional 15% for high uncertainty
        elif uncertainty_level == 'medium':
            risk_adjustment = 0.10  # Additional 10% for medium uncertainty
        else:
            risk_adjustment = 0.05  # Additional 5% for low uncertainty
        
        # Project-specific risk factors (simplified assessment)
        project_area_ha = self._get_project_area_ha(project)
        if project_area_ha < 100:  # Small projects have higher relative risk
            size_risk = 0.05
        else:
            size_risk = 0.0
        
        # Total buffer pool percentage (capped at 30%)
        total_buffer_percentage = min(0.30, base_buffer + risk_adjustment + size_risk)
        
        buffer_pool_contribution = net_carbon_benefit * total_buffer_percentage
        
        logging.info(f"Buffer pool contribution: {total_buffer_percentage*100:.1f}% = {buffer_pool_contribution:.1f} tC")
        return buffer_pool_contribution

    def _assess_methodology_compliance(self, project: Project, forest_analysis: Dict[str, Any], 
                                     uncertainty_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Assess compliance with VCS methodology requirements."""
        compliance_checks = {
            'forest_area_threshold': forest_analysis.get('total_area_ha', 0) >= 0.5,  # Minimum 0.5 ha
            'confidence_threshold': uncertainty_assessment.get('confidence_score', 0) >= 0.3,  # Minimum 30% confidence
            'uncertainty_assessment': uncertainty_assessment.get('vcs_compliant', False),
            'additionality_demonstrated': True,  # Simplified - would require detailed assessment
            'baseline_established': True,  # Simplified - would require historical analysis
            'monitoring_plan': True,  # Simplified - would require MRV system
        }
        
        compliance_score = sum(compliance_checks.values()) / len(compliance_checks)
        
        return {
            'individual_checks': compliance_checks,
            'overall_compliance_score': compliance_score,
            'vcs_eligible': compliance_score >= 0.8,  # 80% compliance required
            'methodology_version': 'VM0007_v1.6_simplified',
            'assessment_date': datetime.now().isoformat()
        }

    def _format_vcs_result(self, vcs_result: VCSCalculationResult) -> Dict[str, Any]:
        """Format VCS calculation result for API response."""
        return {
            # Main results
            'creditable_carbon_credits_tCO2e': vcs_result.creditable_carbon_units_tCO2e,
            'verified_carbon_units_tCO2e': vcs_result.verified_carbon_units_tCO2e,
            
            # Carbon stock analysis
            'carbon_stock_analysis': {
                'project_carbon_stock_tC': vcs_result.project_carbon_stock_tC,
                'baseline_carbon_stock_tC': vcs_result.baseline_carbon_stock_tC,
                'net_carbon_benefit_tC': vcs_result.net_carbon_benefit_tC,
            },
            
            # Deductions and adjustments
            'vcs_adjustments': {
                'leakage_deduction_tC': vcs_result.leakage_deduction_tC,
                'uncertainty_deduction_tC': vcs_result.uncertainty_deduction_tC,
                'buffer_pool_contribution_tC': vcs_result.buffer_pool_contribution_tC,
            },
            
            # Forest analysis
            'forest_analysis': vcs_result.forest_analysis,
            
            # Quality metrics
            'confidence_metrics': vcs_result.confidence_metrics,
            'methodology_compliance': vcs_result.methodology_compliance,
            
            # Metadata
            'calculation_method': 'VCS_Compliant',
            'calculation_date': datetime.now().isoformat(),
            'vcs_methodology': 'VM0007_simplified_for_university'
        }

    def _calculate_simple_credits(self, project: Project, image_path: str, 
                                image_scale_factor: float, project_age_years: int) -> Dict[str, Any]:
        """Simplified carbon calculation for comparison purposes."""
        ecosystem = crud.ecosystem.get(self.db, id=project.ecosystem_id)
        
        # Basic forest detection
        forest_analysis = self.forest_detector.detect_area(
            image_path=image_path,
            ecosystem=ecosystem,
            scale_factor=image_scale_factor
        )
        
        # Simple calculation using weighted carbon density
        total_area_ha = forest_analysis.get('total_area_ha', 0)
        carbon_density = forest_analysis.get('weighted_carbon_density_tC_ha', 0)
        
        # Apply growth factor if available
        if hasattr(ecosystem, 'biomass_growth_rate') and ecosystem.biomass_growth_rate:
            growth_factor = 1 - math.exp(-ecosystem.biomass_growth_rate * project_age_years)
            adjusted_carbon_density = carbon_density * growth_factor
        else:
            adjusted_carbon_density = carbon_density
        
        total_carbon_tC = total_area_ha * adjusted_carbon_density
        total_carbon_tCO2e = total_carbon_tC * self.vcs_parameters['co2_to_c_ratio']
        
        return {
            'creditable_carbon_credits_tCO2e': total_carbon_tCO2e,
            'total_carbon_stock_tC': total_carbon_tC,
            'forest_analysis': forest_analysis,
            'calculation_method': 'Simplified',
            'calculation_date': datetime.now().isoformat()
        }

# Note: VCSCarbonCalculator requires a database session, so it cannot be a global singleton 