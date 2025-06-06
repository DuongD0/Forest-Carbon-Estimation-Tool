# Carbon Calculation Logic - Enhanced for Plot/Species Level

import logging
import math
from typing import Dict, List, Any, Tuple

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from geoalchemy2.types import Geography
import numpy as np
from asteval import Interpreter

# Import all necessary models
from app.models.forest import Forest
from app.models.forest_plot import ForestPlot
from app.models.plot_composition import PlotComposition
from app.models.tree_species import TreeSpecies
from app.models.allometric_equation import AllometricEquation
from app.models.project import Project
from app.models.biomass import Biomass
from app.models.carbon_stock import CarbonStock
from app.models.baseline import Baseline
from app.models.carbon_credit import CarbonCredit

logger = logging.getLogger(__name__)

# --- Standard Conversion Factors (from IPCC guidelines) ---
IPCC_ROOT_TO_SHOOT_RATIO = 0.26  # For tropical forests
IPCC_CARBON_FRACTION = 0.47      # Fraction of carbon in dry biomass
CO2_CONVERSION_FACTOR = 44 / 12  # Molar mass ratio of CO2 to C

# --- VCS Methodology Default Parameters (can be overridden by project specifics) ---
DEFAULT_LEAKAGE_FACTOR = 0.10 # 10%
DEFAULT_PERMANENCE_BUFFER = 0.15 # 15% risk buffer

class CarbonCalculator:
    """
    Handles the end-to-end carbon credit calculation process,
    aligning with the detailed carbon calculation design document.
    """

    def __init__(self, db_session: Session, project_id: int):
        self.db = db_session
        self.project_id = project_id
        self.project = self.db.query(Project).get(self.project_id)
        if not self.project:
            raise ValueError(f"Project with ID {project_id} not found.")
        # Use a safe interpreter for evaluating formulas
        self.aeval = Interpreter()

    def run_full_calculation(self) -> List[Dict[str, Any]]:
        """
        Orchestrates the full calculation pipeline for all forests in the project.
        Returns a summary of the results for each forest.
        """
        results_summary = []
        forests = self.db.query(Forest).filter(Forest.project_id == self.project_id).all()
        
        if not forests:
            raise ValueError("No forests found for this project.")

        for forest in forests:
            try:
                biomass, carbon_stock = self._calculate_forest_stock(forest)
                baseline = self._establish_forest_baseline(forest, carbon_stock)
                credits = self._quantify_credits(carbon_stock, baseline)
                results_summary.append({
                    "forest_id": forest.forest_id,
                    "status": "Success",
                    "credit_id": credits.credit_id
                })
            except Exception as e:
                logger.error(f"Failed to calculate carbon for forest {forest.forest_id}: {e}", exc_info=True)
                results_summary.append({
                    "forest_id": forest.forest_id,
                    "status": "Failed",
                    "error": str(e)
                })
        return results_summary

    def _calculate_forest_stock(self, forest: Forest) -> Tuple[Biomass, CarbonStock]:
        """
        Calculates total biomass and carbon stock for a single forest.
        It aggregates plot data if available.
        """
        total_agb = 0.0
        # Eager load related data to avoid N+1 query problems
        plots = self.db.query(ForestPlot).filter(ForestPlot.forest_id == forest.forest_id).options(
            joinedload(ForestPlot.plot_compositions).joinedload(PlotComposition.species)
        ).all()

        if not plots:
            raise ValueError(f"No forest plots found for forest {forest.forest_name}. Cannot perform calculation.")

        for plot in plots:
            plot_agb, _ = self._calculate_biomass_for_plot(plot)
            total_agb += plot_agb # Assuming plot_agb is for the whole plot area

        # Calculate BGB and total biomass
        total_bgb = total_agb * IPCC_ROOT_TO_SHOOT_RATIO
        total_biomass_tonnes = total_agb + total_bgb
        
        # Save biomass results
        biomass_record = Biomass(
            project_id=self.project_id,
            forest_id=forest.forest_id,
            agb_total=total_agb,
            bgb_total=total_bgb,
            total_biomass=total_biomass_tonnes
        )
        self.db.add(biomass_record)
        self.db.flush()

        # Convert biomass to carbon stock
        agb_carbon = total_agb * IPCC_CARBON_FRACTION
        bgb_carbon = total_bgb * IPCC_CARBON_FRACTION
        total_carbon = total_biomass_tonnes * IPCC_CARBON_FRACTION
        total_co2e = total_carbon * CO2_CONVERSION_FACTOR
        
        # Save carbon stock results
        carbon_stock_record = CarbonStock(
            biomass_id=biomass_record.biomass_id,
            project_id=self.project_id,
            forest_id=forest.forest_id,
            agb_carbon=agb_carbon,
            bgb_carbon=bgb_carbon,
            total_carbon=total_carbon,
            agb_co2e=agb_carbon * CO2_CONVERSION_FACTOR,
            bgb_co2e=bgb_carbon * CO2_CONVERSION_FACTOR,
            total_co2e=total_co2e
        )
        self.db.add(carbon_stock_record)
        self.db.flush()

        return biomass_record, carbon_stock_record

    def _calculate_biomass_for_plot(self, plot: ForestPlot) -> Tuple[float, float]:
        """Calculates Above-Ground Biomass (AGB) for a single plot."""
        plot_agb = 0.0
        
        for comp in plot.plot_compositions:
            if not all([comp.average_dbh, comp.stem_density, comp.species, comp.species.wood_density]):
                logger.warning(f"Skipping plot composition {comp.plot_composition_id} due to missing data.")
                continue

            species = comp.species
            equation = self._get_equation_for_species(species)
            
            # Parameters for the formula
            params = {
                'DBH': comp.average_dbh,
                'WD': species.wood_density,
                'H': comp.average_height or 0 # Pass height if available
            }
            
            # Calculate AGB for a single tree
            agb_per_tree_kg = self._evaluate_biomass_formula(equation.equation_formula, params)
            
            # Extrapolate to the plot area
            # Assuming stem_density is trees per hectare, and plot area is in hectares
            plot_area_ha = (plot.geometry.area / 10000) if plot.geometry else 0
            if plot_area_ha > 0:
                 # AGB in tonnes for the species in the plot
                plot_agb += (agb_per_tree_kg / 1000) * comp.stem_density * plot_area_ha

        return plot_agb, 0.0 # Returning AGB and BGB for consistency, but BGB is calculated at forest level

    def _get_equation_for_species(self, species: TreeSpecies) -> AllometricEquation:
        """Finds the most appropriate allometric equation for a species."""
        # Prioritize the species' default equation
        if species.default_allometric_equation_id:
            eq = self.db.query(AllometricEquation).get(species.default_allometric_equation_id)
            if eq: return eq
        
        # Fallback logic (e.g., find a generic equation for the region/type)
        # This can be made more sophisticated
        fallback_eq = self.db.query(AllometricEquation).filter(
            AllometricEquation.region == "Pantropical"
        ).first()

        if not fallback_eq:
            raise ValueError(f"No suitable allometric equation found for species {species.scientific_name} or as a fallback.")
            
        return fallback_eq

    def _evaluate_biomass_formula(self, formula: str, params: Dict[str, float]) -> float:
        """Safely evaluates a formula string with given parameters."""
        self.aeval.symtable.update(params)
        try:
            # Formula is expected to return biomass in kg
            result = self.aeval.eval(formula)
            if not isinstance(result, (int, float)):
                raise ValueError("Formula did not evaluate to a number.")
            return result
        except Exception as e:
            logger.error(f"Failed to evaluate formula '{formula}' with params {params}: {e}")
            raise

    def _establish_forest_baseline(self, forest: Forest, carbon_stock: CarbonStock) -> Baseline:
        """
        Establishes a baseline for the forest.
        Placeholder logic: assumes a simple baseline of 20% less than current stock.
        In a real scenario, this would use historical data or deforestation models.
        """
        baseline_co2e = carbon_stock.total_co2e * 0.80 # Assume 20% deforestation/degradation rate
        
        baseline_record = Baseline(
            project_id=self.project_id,
            forest_id=forest.forest_id,
            baseline_type="Simplified Historical",
            baseline_co2e=baseline_co2e,
            parameters={"method": "20% reduction from current stock"}
        )
        self.db.add(baseline_record)
        self.db.flush()
        return baseline_record

    def _quantify_credits(self, carbon_stock: CarbonStock, baseline: Baseline) -> CarbonCredit:
        """
        Quantifies net carbon credits based on stock, baseline, and deductions
        following VCS/REDD+ principles.
        """
        gross_reduction = carbon_stock.total_co2e - baseline.baseline_co2e
        if gross_reduction <= 0:
            gross_reduction = 0

        # Account for leakage
        leakage_deduction = gross_reduction * DEFAULT_LEAKAGE_FACTOR
        net_reduction = gross_reduction - leakage_deduction

        # Account for permanence risk buffer
        buffer_deduction = net_reduction * DEFAULT_PERMANENCE_BUFFER
        issuable_credits = net_reduction - buffer_deduction
        
        credit_record = CarbonCredit(
            project_id=self.project_id,
            forest_id=carbon_stock.forest_id,
            carbon_id=carbon_stock.carbon_id,
            baseline_id=baseline.baseline_id,
            emission_reduction_co2e=gross_reduction,
            leakage_deduction=leakage_deduction,
            buffer_amount=buffer_deduction,
            creditable_amount=issuable_credits if issuable_credits > 0 else 0,
            methodology="VCS/IPCC Simplified"
        )
        self.db.add(credit_record)
        self.db.commit() # Commit the transaction for this forest's full calculation
        return credit_record


