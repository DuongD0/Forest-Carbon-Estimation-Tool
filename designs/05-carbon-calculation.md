# Carbon Calculation Engine

## Overview

The Carbon Calculation Engine is the core scientific component of the Forest Carbon Credit Estimation Tool, responsible for converting forest area measurements into accurate carbon credit estimations. This module implements internationally recognized methodologies for biomass estimation, carbon stock calculation, and carbon credit quantification in compliance with REDD+ and VCS standards.

## Functional Requirements

### Primary Functions
1. **Biomass Estimation**: Calculate above and below-ground biomass using allometric equations
2. **Carbon Stock Calculation**: Convert biomass to carbon stock using standard conversion factors
3. **Carbon Credit Quantification**: Apply methodological standards to determine tradeable credits
4. **Uncertainty Analysis**: Calculate confidence intervals and error margins
5. **Baseline Comparison**: Compare current carbon stocks with historical baselines
6. **Additionality Assessment**: Evaluate carbon additionality against business-as-usual scenarios

### Performance Requirements
- Support for multiple international carbon accounting methodologies
- Accuracy within ±15% of expert assessments
- Uncertainty quantification with statistical confidence levels
- Processing of up to 1,000 forest polygons per calculation
- Calculation time under 5 seconds for typical forest areas

## Technical Design

### Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                 Carbon Calculation Engine                   │
│                                                            │
│  ┌────────────────┐   ┌────────────────┐  ┌───────────────┐│
│  │    Biomass     │   │    Carbon      │  │    Credit     ││
│  │   Calculator   │──▶│   Converter    │─▶│  Quantifier   ││
│  └────────────────┘   └────────────────┘  └───────────────┘│
│          │                   │                   │         │
│          ▼                   ▼                   ▼         │
│  ┌────────────────┐   ┌────────────────┐  ┌───────────────┐│
│  │  Uncertainty   │   │   Baseline     │  │ Additionality ││
│  │   Analyzer     │   │   Comparator   │  │  Assessor     ││
│  └────────────────┘   └────────────────┘  └───────────────┘│
└────────────────────────────────────────────────────────────┘
```

### Subcomponents

#### 1. Biomass Calculator
- **Allometric Equation Library**: Collection of validated equations for Vietnamese forests
- **Forest Type Matching**: Apply appropriate equations based on forest classification
- **Above-Ground Biomass (AGB)**: Calculate tree and vegetation biomass above ground
- **Below-Ground Biomass (BGB)**: Estimate root systems using root-to-shoot ratios
- **Wood Density Database**: Vietnamese tree species with specific wood density values

#### 2. Carbon Converter
- **Carbon Fraction Application**: Convert biomass to carbon using standard fractions
- **Carbon Pool Aggregation**: Combine multiple carbon pools (trees, soil, deadwood)
- **CO₂ Equivalent Calculation**: Convert carbon to CO₂e using molecular weight ratios
- **Time-series Integration**: Track carbon stock changes over time

#### 3. Credit Quantifier
- **Methodology Implementation**: REDD+, VCS, and other standard methodologies
- **Leakage Assessment**: Account for displaced deforestation or degradation
- **Permanence Risk Analysis**: Evaluate risk of non-permanence
- **Buffer Determination**: Calculate buffer withholding based on risk assessment

#### 4. Uncertainty Analyzer
- **Error Propagation**: Combine uncertainties from multiple measurement sources
- **Monte Carlo Simulation**: Probabilistic assessment of overall uncertainty
- **Confidence Interval Calculation**: Determine statistical confidence levels
- **Sensitivity Analysis**: Identify key factors influencing uncertainty

#### 5. Baseline Comparator
- **Historical Baseline Creation**: Establish reference levels from historical data
- **Projected Baseline Modeling**: Model business-as-usual scenarios
- **Difference Calculation**: Quantify improvements against baseline
- **Trend Analysis**: Evaluate carbon stock changes over time

#### 6. Additionality Assessor
- **Regulatory Surplus Test**: Verify exceeding legal requirements
- **Common Practice Analysis**: Compare against standard industry practices
- **Financial Additionality**: Assess economic viability without carbon credits
- **Barrier Analysis**: Identify obstacles to implementation without intervention

## Detailed Algorithms

### Biomass Estimation Algorithm

```python
def calculate_biomass(forest_data, allometric_params):
    """
    Calculate forest biomass using allometric equations appropriate for Vietnamese forests.
    
    Args:
        forest_data (dict): Dictionary containing forest classification and area data
        allometric_params (dict): Parameters for allometric equations by forest type
        
    Returns:
        dict: Calculated biomass values (AGB, BGB, total) in tonnes
    """
    results = {}
    
    # Process each forest polygon
    for forest_id, forest_info in forest_data.items():
        forest_type = forest_info['forest_type']
        area_ha = forest_info['area_ha']
        
        # Get appropriate parameters for this forest type
        if forest_type not in allometric_params:
            raise ValueError(f"No allometric parameters available for forest type: {forest_type}")
        
        params = allometric_params[forest_type]
        
        # Calculate Above-Ground Biomass using appropriate equation
        # This implementation uses the general form from Chave et al. (2014)
        # with parameters calibrated for Vietnamese forests
        agb_per_ha = params['a'] * (area_ha ** params['b'])
        
        # Apply correction factor based on forest condition if available
        if 'condition' in forest_info:
            condition = forest_info['condition']
            condition_factor = params.get('condition_factors', {}).get(condition, 1.0)
            agb_per_ha *= condition_factor
        
        # Calculate total AGB for this forest area
        agb_total = agb_per_ha * area_ha
        
        # Calculate Below-Ground Biomass using root-to-shoot ratio
        bgb_total = agb_total * params['root_shoot_ratio']
        
        # Store results
        results[forest_id] = {
            'forest_type': forest_type,
            'area_ha': area_ha,
            'agb_per_ha': agb_per_ha,
            'agb_total': agb_total,
            'bgb_total': bgb_total,
            'total_biomass': agb_total + bgb_total
        }
    
    return results
```

### Carbon Stock Calculation Algorithm

```python
def calculate_carbon_stock(biomass_data):
    """
    Convert biomass to carbon stock using standard conversion factors.
    
    Args:
        biomass_data (dict): Dictionary containing biomass calculations
        
    Returns:
        dict: Carbon stock values in tonnes of carbon and CO₂ equivalent
    """
    # Standard carbon fraction for tropical forests (IPCC default)
    CARBON_FRACTION = 0.47
    
    # Molecular weight ratio of CO₂ to C (44/12)
    CO2_CONVERSION_FACTOR = 44/12
    
    results = {}
    
    for forest_id, biomass_info in biomass_data.items():
        # Extract biomass values
        agb_total = biomass_info['agb_total']
        bgb_total = biomass_info['bgb_total']
        total_biomass = biomass_info['total_biomass']
        
        # Convert biomass to carbon
        agb_carbon = agb_total * CARBON_FRACTION
        bgb_carbon = bgb_total * CARBON_FRACTION
        total_carbon = total_biomass * CARBON_FRACTION
        
        # Convert carbon to CO₂ equivalent
        agb_co2e = agb_carbon * CO2_CONVERSION_FACTOR
        bgb_co2e = bgb_carbon * CO2_CONVERSION_FACTOR
        total_co2e = total_carbon * CO2_CONVERSION_FACTOR
        
        # Store results
        results[forest_id] = {
            'forest_type': biomass_info['forest_type'],
            'area_ha': biomass_info['area_ha'],
            'agb_carbon': agb_carbon,
            'bgb_carbon': bgb_carbon,
            'total_carbon': total_carbon,
            'agb_co2e': agb_co2e,
            'bgb_co2e': bgb_co2e,
            'total_co2e': total_co2e,
            'carbon_density': total_carbon / biomass_info['area_ha']  # tC/ha
        }
    
    return results
```

### Carbon Credit Calculation Algorithm

```python
def calculate_carbon_credits(carbon_data, baseline_data, methodology_params):
    """
    Calculate carbon credits based on specified methodology.
    
    Args:
        carbon_data (dict): Current carbon stock data
        baseline_data (dict): Baseline carbon stock data
        methodology_params (dict): Parameters for the selected methodology
        
    Returns:
        dict: Calculated carbon credits with uncertainty and buffer
    """
    # Extract methodology settings
    methodology = methodology_params['name']
    buffer_percentage = methodology_params['buffer_percentage']
    leakage_factor = methodology_params.get('leakage_factor', 0)
    uncertainty_threshold = methodology_params.get('uncertainty_threshold', 15)
    
    results = {}
    total_emission_reduction = 0
    
    for forest_id, carbon_info in carbon_data.items():
        # Get baseline carbon for this forest
        if forest_id not in baseline_data:
            continue
            
        baseline_carbon = baseline_data[forest_id]['total_carbon']
        current_carbon = carbon_info['total_carbon']
        
        # Calculate emission reduction (carbon stock change)
        emission_reduction = current_carbon - baseline_carbon
        
        # Apply leakage discount if applicable
        emission_reduction *= (1 - leakage_factor)
        
        # Convert to CO₂ equivalent
        emission_reduction_co2e = emission_reduction * (44/12)
        
        # Calculate uncertainty
        uncertainty = calculate_uncertainty(carbon_info, baseline_data[forest_id])
        
        # Apply uncertainty deduction if above threshold
        if uncertainty > uncertainty_threshold:
            uncertainty_deduction = (uncertainty - uncertainty_threshold) / 100
            emission_reduction_co2e *= (1 - uncertainty_deduction)
        
        # Apply buffer withholding
        buffer_amount = emission_reduction_co2e * (buffer_percentage / 100)
        creditable_amount = emission_reduction_co2e - buffer_amount
        
        # Store results
        results[forest_id] = {
            'forest_type': carbon_info['forest_type'],
            'area_ha': carbon_info['area_ha'],
            'baseline_carbon': baseline_carbon,
            'current_carbon': current_carbon,
            'emission_reduction': emission_reduction,
            'emission_reduction_co2e': emission_reduction_co2e,
            'uncertainty_percentage': uncertainty,
            'buffer_amount': buffer_amount,
            'creditable_amount': creditable_amount
        }
        
        total_emission_reduction += creditable_amount
    
    # Add summary
    results['summary'] = {
        'methodology': methodology,
        'total_creditable_amount': total_emission_reduction,
        'buffer_percentage': buffer_percentage,
        'total_buffer_amount': sum(r['buffer_amount'] for r in results.values() if isinstance(r, dict) and 'buffer_amount' in r),
        'average_uncertainty': sum(r['uncertainty_percentage'] for r in results.values() if isinstance(r, dict) and 'uncertainty_percentage' in r) / len([r for r in results.values() if isinstance(r, dict) and 'uncertainty_percentage' in r]) if results else 0
    }
    
    return results
```

## Allometric Equations for Vietnamese Forests

The Carbon Calculation Engine employs scientifically validated allometric equations specific to Vietnamese forest ecosystems. These equations have been calibrated based on extensive field measurements and research.

### Above-Ground Biomass Equations

| Forest Type | Equation | Parameters | Source |
|-------------|----------|------------|--------|
| Tropical Evergreen | AGB = 0.0509 × ρ × DBH² × H | ρ: wood density, DBH: diameter at breast height, H: height | Chave et al. (2014) |
| Deciduous | AGB = 0.0673 × (ρ × DBH² × H)^0.976 | ρ: wood density, DBH: diameter at breast height, H: height | Ketterings et al. (2001) |
| Mangrove | AGB = 0.251 × ρ × DBH^2.46 | ρ: wood density, DBH: diameter at breast height | Komiyama et al. (2008) |
| Bamboo | AGB = 0.131 × DBH^2.28 | DBH: diameter at breast height | Yen et al. (2010) |

### Root-to-Shoot Ratios

| Forest Type | Root-to-Shoot Ratio | Source |
|-------------|---------------------|--------|
| Tropical Evergreen | 0.24 | IPCC (2006) |
| Deciduous | 0.26 | IPCC (2006) |
| Mangrove | 0.38 | Komiyama et al. (2008) |
| Bamboo | 0.20 | Yen et al. (2010) |

### Wood Density Values

The system includes a database of wood density values for Vietnamese tree species. Average values by forest type:

| Forest Type | Average Wood Density (g/cm³) |
|-------------|------------------------------|
| Tropical Evergreen | 0.57 |
| Deciduous | 0.54 |
| Mangrove | 0.71 |
| Bamboo | 0.60 |

## Carbon Calculation Methodologies

### Supported Methodologies

The system supports multiple carbon accounting methodologies:

1. **VCS VM0015**: "Methodology for Avoided Unplanned Deforestation"
2. **VCS VM0007**: "REDD+ Methodology Framework"
3. **CDM AR-ACM0003**: "Afforestation and Reforestation of Lands Except Wetlands"
4. **Vietnam REDD+**: Vietnam-specific REDD+ methodological framework

### Methodology Parameters

Each methodology has specific parameters that affect carbon credit calculations:

#### VCS VM0015
- Buffer Pool: 10-20% (risk-based)
- Leakage Factor: 0-40% (project-specific)
- Uncertainty Threshold: 15%
- Crediting Period: 20-100 years

#### VCS VM0007
- Buffer Pool: 10-30% (risk-based)
- Leakage Factor: 0-40% (project-specific)
- Uncertainty Threshold: 15%
- Crediting Period: 20-100 years

#### CDM AR-ACM0003
- Buffer Pool: Not applicable
- Leakage Factor: Project-specific
- Uncertainty Threshold: 10%
- Crediting Period: 20-60 years

#### Vietnam REDD+
- Buffer Pool: 15% (default)
- Leakage Factor: 20% (default)
- Uncertainty Threshold: 15%
- Crediting Period: 10-30 years

## Uncertainty Analysis

### Sources of Uncertainty

The system quantifies uncertainty from multiple sources:

1. **Measurement Uncertainty**: Related to area calculation, image classification
2. **Allometric Uncertainty**: Error in biomass equations
3. **Sampling Uncertainty**: When using sample plots for calibration
4. **Model Uncertainty**: In baseline and projection models

### Uncertainty Calculation Methods

```python
def calculate_uncertainty(carbon_data, baseline_data):
    """
    Calculate combined uncertainty for carbon stock estimates.
    
    Args:
        carbon_data (dict): Current carbon stock data with uncertainty values
        baseline_data (dict): Baseline carbon stock data with uncertainty values
        
    Returns:
        float: Combined uncertainty percentage
    """
    # Extract uncertainty values
    measurement_uncertainty = carbon_data.get('measurement_uncertainty', 5)  # Default 5%
    allometric_uncertainty = carbon_data.get('allometric_uncertainty', 10)  # Default 10%
    sampling_uncertainty = carbon_data.get('sampling_uncertainty', 8)  # Default 8%
    model_uncertainty = baseline_data.get('model_uncertainty', 12)  # Default 12%
    
    # Calculate combined uncertainty using error propagation formula
    # (square root of sum of squares)
    combined_uncertainty = math.sqrt(
        measurement_uncertainty**2 + 
        allometric_uncertainty**2 + 
        sampling_uncertainty**2 + 
        model_uncertainty**2
    )
    
    return combined_uncertainty
```

### Monte Carlo Simulation

For comprehensive uncertainty analysis, the system also employs Monte Carlo simulation:

```python
def monte_carlo_uncertainty(carbon_data, baseline_data, num_simulations=1000):
    """
    Perform Monte Carlo simulation to estimate overall uncertainty.
    
    Args:
        carbon_data (dict): Current carbon stock data
        baseline_data (dict): Baseline carbon stock data
        num_simulations (int): Number of Monte Carlo simulations
        
    Returns:
        dict: Uncertainty statistics including confidence intervals
    """
    # Define uncertainty distributions for parameters
    distributions = {
        'area': ('normal', carbon_data['area_ha'], carbon_data.get('area_uncertainty', 0.05) * carbon_data['area_ha']),
        'agb_factor': ('normal', 1.0, carbon_data.get('allometric_uncertainty', 0.1)),
        'carbon_fraction': ('normal', 0.47, 0.02),
        'root_shoot_ratio': ('normal', carbon_data.get('root_shoot_ratio', 0.24), 0.05),
        'baseline': ('normal', baseline_data['total_carbon'], baseline_data.get('model_uncertainty', 0.12) * baseline_data['total_carbon'])
    }
    
    # Run simulations
    results = []
    
    for _ in range(num_simulations):
        # Generate random values from distributions
        sim_values = {}
        for param, (dist_type, mean, std) in distributions.items():
            if dist_type == 'normal':
                sim_values[param] = np.random.normal(mean, std)
            elif dist_type == 'lognormal':
                sim_values[param] = np.random.lognormal(np.log(mean), std)
        
        # Calculate carbon stock for this simulation
        sim_agb = sim_values['area'] * carbon_data['agb_per_ha'] * sim_values['agb_factor']
        sim_bgb = sim_agb * sim_values['root_shoot_ratio']
        sim_total_carbon = (sim_agb + sim_bgb) * sim_values['carbon_fraction']
        sim_emission_reduction = sim_total_carbon - sim_values['baseline']
        sim_co2e = sim_emission_reduction * (44/12)
        
        results.append(sim_co2e)
    
    # Calculate statistics
    mean_co2e = np.mean(results)
    std_co2e = np.std(results)
    ci_95_lower = np.percentile(results, 2.5)
    ci_95_upper = np.percentile(results, 97.5)
    
    # Calculate uncertainty as percentage
    uncertainty_percentage = (std_co2e / mean_co2e) * 100 if mean_co2e != 0 else 0
    
    return {
        'mean_co2e': mean_co2e,
        'std_co2e': std_co2e,
        'uncertainty_percentage': uncertainty_percentage,
        'ci_95_lower': ci_95_lower,
        'ci_95_upper': ci_95_upper,
        'simulation_count': num_simulations
    }
```

## Baseline and Additionality

### Baseline Approaches

The system supports multiple baseline approaches:

1. **Historical Average**: Based on historical deforestation rates
2. **Projected Trend**: Using statistical models to project trends
3. **Reference Region**: Using a similar region as reference
4. **Fixed Reference Level**: Using nationally determined reference levels

### Additionality Tests

For each project, additionality is assessed through:

1. **Regulatory Surplus Test**: Verifying the project exceeds legal requirements
2. **Common Practice Analysis**: Comparing against standard practices
3. **Investment Analysis**: Determining financial viability without carbon credits
4. **Barrier Analysis**: Identifying implementation obstacles

## Input Requirements

### Forest Data Input
- Forest classification by type
- Area measurements in hectares
- Condition assessment (if available)
- Geospatial boundaries

### Baseline Data Input
- Historical carbon stock data
- Reference period definition
- Projected baseline parameters
- National/regional reference levels

### Methodology Parameters
- Selected methodology
- Risk assessment for buffer determination
- Leakage assessment factors
- Crediting period definition

## Output Specifications

### Carbon Credit Results
- Total emission reductions (tCO₂e)
- Buffer withholding amount
- Creditable carbon amount
- Project lifetime projections

### Uncertainty Analysis
- Combined uncertainty percentage
- Confidence intervals
- Sensitivity analysis results
- Monte Carlo simulation statistics

### Verification Documentation
- Methodology compliance report
- Additionality assessment
- Baseline justification
- Leakage assessment

## Error Handling

### Common Error Scenarios
1. **Missing Data**: System will identify required data fields
2. **Methodology Mismatch**: Will verify project eligibility for selected methodology
3. **Excessive Uncertainty**: Will flag if uncertainty exceeds acceptable thresholds
4. **Negative Emission Reductions**: Will alert if current carbon is below baseline
5. **Parameter Out of Range**: Will validate input parameters against acceptable ranges

### Error Response Strategy
- Detailed error messages with specific validation failures
- Recommendations for data improvement
- Fallback to conservative defaults when appropriate
- Warning system for potential methodology compliance issues

## Performance Optimization

### Computational Optimization
- **Batch Processing**: Calculate multiple forest areas simultaneously
- **Caching**: Store intermediate calculation results
- **Parallel Processing**: Utilize multiple cores for Monte Carlo simulations
- **Resource Management**: Optimize memory usage for large datasets

### Resource Requirements
- **CPU**: Multi-core processor recommended for uncertainty analysis
- **RAM**: 8GB minimum, 16GB recommended for large projects
- **Storage**: Minimal requirements for calculation engine itself
- **Database**: Connection to PostgreSQL for data retrieval and storage

## Testing and Validation

### Unit Testing
- Tests for each calculation component
- Verification against known reference values
- Edge case testing for parameter ranges

### Integration Testing
- End-to-end testing with real project data
- Cross-validation with established carbon calculators
- Methodology compliance validation

### Validation Methodology
- Comparison with field-measured carbon stock
- Verification against published case studies
- Expert review by carbon accounting specialists

## Implementation Guidelines

### Development Standards
- Follow PEP 8 style guide for Python code
- Document all functions with docstrings
- Implement type hints for better code clarity
- Maintain comprehensive test coverage

### Dependencies
- NumPy for numerical operations
- SciPy for statistical functions
- Pandas for data manipulation
- Matplotlib/Seaborn for result visualization (optional)

### Integration Points
- **Input**: Geospatial Processing Module
- **Output**: Report Generator
- **Storage**: PostgreSQL Database
- **API**: RESTful Services for web integration

## Code Examples

### Complete Carbon Calculation Pipeline

```python
def calculate_carbon_credits_pipeline(forest_data, project_params):
    """
    Complete pipeline for carbon credit calculation.
    
    Args:
        forest_data (dict): Dictionary containing forest classification and area data
        project_params (dict): Project parameters including methodology selection
        
    Returns:
        dict: Carbon credit calculation results
    """
    # 1. Extract parameters
    methodology = project_params['methodology']
    baseline_type = project_params['baseline_type']
    crediting_period = project_params['crediting_period']
    
    # 2. Load appropriate allometric parameters
    allometric_params = load_allometric_parameters(methodology)
    
    # 3. Calculate biomass
    biomass_results = calculate_biomass(forest_data, allometric_params)
    
    # 4. Calculate carbon stocks
    carbon_results = calculate_carbon_stock(biomass_results)
    
    # 5. Determine baseline
    baseline_results = calculate_baseline(
        forest_data, 
        carbon_results,
        baseline_type, 
        project_params
    )
    
    # 6. Calculate emission reductions
    credit_results = calculate_carbon_credits(
        carbon_results, 
        baseline_results, 
        project_params
    )
    
    # 7. Perform uncertainty analysis
    uncertainty_results = monte_carlo_uncertainty(
        carbon_results, 
        baseline_results
    )
    
    # 8. Assess additionality
    additionality_results = assess_additionality(
        carbon_results,
        baseline_results,
        project_params
    )
    
    # 9. Generate final results
    final_results = {
        'project_info': {
            'name': project_params.get('name', 'Unnamed Project'),
            'methodology': methodology,
            'crediting_period': crediting_period,
            'baseline_type': baseline_type
        },
        'carbon_stocks': carbon_results,
        'baseline': baseline_results,
        'emission_reductions': credit_results,
        'uncertainty': uncertainty_results,
        'additionality': additionality_results,
        'total_credits': credit_results['summary']['total_creditable_amount'],
        'total_buffer': credit_results['summary']['total_buffer_amount'],
        'average_uncertainty': credit_results['summary']['average_uncertainty']
    }
    
    return final_results
```

This detailed documentation provides a comprehensive guide for implementing the Carbon Calculation Engine, covering algorithms, methodologies, and integration guidelines for development teams.