import pytest
from unittest.mock import MagicMock, patch
from app.processing.carbon_calculator import (
    CarbonCalculator,
    calculate_biomass,
    calculate_carbon_stock,
    calculate_carbon_credits,
    apply_uncertainty_factor
)
import numpy as np

# Test the CarbonCalculator class
class TestCarbonCalculator:
    
    @pytest.fixture
    def calculator(self):
        return CarbonCalculator()
    
    @pytest.fixture
    def sample_forest_data(self):
        # Create sample forest data
        return {
            'area_ha': 1000,
            'forest_type': 'TROPICAL_EVERGREEN',
            'age_years': 30,
            'canopy_density': 0.8,
            'elevation_m': 500,
            'region': 'amazon'
        }
    
    @pytest.fixture
    def sample_ndvi_data(self):
        # Create a sample NDVI array
        return np.random.uniform(0.2, 0.9, (100, 100))
    
    def test_init(self, calculator):
        """Test that the CarbonCalculator initializes correctly"""
        assert calculator.supported_methods == ['standard', 'enhanced', 'detailed']
        assert calculator.biomass_factors is not None
        assert 'TROPICAL_EVERGREEN' in calculator.biomass_factors
        assert calculator.carbon_fraction == 0.47
        assert calculator.co2_equivalent_factor == 3.67
    
    def test_validate_inputs_valid(self, calculator, sample_forest_data):
        """Test input validation with valid data"""
        result = calculator.validate_inputs(sample_forest_data, 'standard')
        assert result is True
    
    def test_validate_inputs_invalid_method(self, calculator, sample_forest_data):
        """Test input validation with invalid method"""
        with pytest.raises(ValueError) as excinfo:
            calculator.validate_inputs(sample_forest_data, 'invalid_method')
        assert "Unsupported calculation method" in str(excinfo.value)
    
    def test_validate_inputs_missing_data(self, calculator):
        """Test input validation with missing data"""
        # Missing required fields
        incomplete_data = {
            'area_ha': 1000,
            # Missing forest_type
            'age_years': 30
        }
        
        with pytest.raises(ValueError) as excinfo:
            calculator.validate_inputs(incomplete_data, 'standard')
        assert "Missing required forest data" in str(excinfo.value)
    
    def test_calculate_carbon_standard(self, calculator, sample_forest_data):
        """Test standard carbon calculation method"""
        # Mock the internal calculation methods
        calculator.calculate_biomass = MagicMock(return_value=200)
        calculator.calculate_carbon_stock = MagicMock(return_value=94)
        calculator.calculate_carbon_credits = MagicMock(return_value=345)
        
        result = calculator.calculate_carbon(sample_forest_data, 'standard')
        
        # Verify methods were called
        calculator.calculate_biomass.assert_called_once()
        calculator.calculate_carbon_stock.assert_called_once()
        calculator.calculate_carbon_credits.assert_called_once()
        
        # Check result structure
        assert 'biomass_tons' in result
        assert 'carbon_stock_tons' in result
        assert 'carbon_credits_tons' in result
        assert 'method' in result
        assert result['method'] == 'standard'
        
        # Check values
        assert result['biomass_tons'] == 200
        assert result['carbon_stock_tons'] == 94
        assert result['carbon_credits_tons'] == 345
    
    def test_calculate_carbon_enhanced(self, calculator, sample_forest_data, sample_ndvi_data):
        """Test enhanced carbon calculation method with NDVI data"""
        # Add NDVI data to forest data
        enhanced_data = sample_forest_data.copy()
        enhanced_data['ndvi_data'] = sample_ndvi_data
        
        # Mock the internal calculation methods
        calculator.calculate_biomass = MagicMock(return_value=200)
        calculator.calculate_carbon_stock = MagicMock(return_value=94)
        calculator.calculate_carbon_credits = MagicMock(return_value=345)
        calculator.apply_ndvi_adjustment = MagicMock(return_value=220)  # Enhanced biomass
        
        result = calculator.calculate_carbon(enhanced_data, 'enhanced')
        
        # Verify methods were called
        calculator.calculate_biomass.assert_called_once()
        calculator.apply_ndvi_adjustment.assert_called_once()
        calculator.calculate_carbon_stock.assert_called_once()
        calculator.calculate_carbon_credits.assert_called_once()
        
        # Check result structure
        assert 'biomass_tons' in result
        assert 'carbon_stock_tons' in result
        assert 'carbon_credits_tons' in result
        assert 'method' in result
        assert result['method'] == 'enhanced'
        
        # Check that NDVI adjustment was applied
        assert 'ndvi_adjustment_factor' in result
    
    def test_calculate_biomass(self, calculator, sample_forest_data):
        """Test biomass calculation"""
        # For tropical evergreen forest with 1000 ha and 0.8 canopy density
        # Expected biomass = area_ha * biomass_factor * canopy_density
        # Assuming biomass_factor for TROPICAL_EVERGREEN is 250
        expected_biomass = 1000 * 250 * 0.8
        
        biomass = calculator.calculate_biomass(sample_forest_data)
        
        # Check value
        assert abs(biomass - expected_biomass) < 1e-6
    
    def test_calculate_carbon_stock(self, calculator):
        """Test carbon stock calculation"""
        biomass = 200000  # 200,000 tons
        
        # Expected carbon stock = biomass * carbon_fraction
        # Carbon fraction is 0.47
        expected_carbon_stock = biomass * 0.47
        
        carbon_stock = calculator.calculate_carbon_stock(biomass)
        
        # Check value
        assert abs(carbon_stock - expected_carbon_stock) < 1e-6
    
    def test_calculate_carbon_credits(self, calculator):
        """Test carbon credits calculation"""
        carbon_stock = 94000  # 94,000 tons
        
        # Expected carbon credits = carbon_stock * co2_equivalent_factor
        # CO2 equivalent factor is 3.67
        expected_carbon_credits = carbon_stock * 3.67
        
        carbon_credits = calculator.calculate_carbon_credits(carbon_stock)
        
        # Check value
        assert abs(carbon_credits - expected_carbon_credits) < 1e-6
    
    def test_apply_ndvi_adjustment(self, calculator, sample_ndvi_data):
        """Test NDVI adjustment to biomass"""
        biomass = 200000  # 200,000 tons
        
        # Mock the mean NDVI calculation
        with patch('numpy.mean') as mock_mean:
            mock_mean.return_value = 0.7  # High NDVI value
            
            adjusted_biomass = calculator.apply_ndvi_adjustment(biomass, sample_ndvi_data)
            
            # Check that adjustment was applied (should increase biomass for high NDVI)
            assert adjusted_biomass > biomass
    
    def test_apply_uncertainty_factor(self, calculator):
        """Test uncertainty factor application"""
        carbon_credits = 345000  # 345,000 tons
        uncertainty_level = 'high'
        
        # Apply uncertainty factor
        adjusted_credits = calculator.apply_uncertainty_factor(carbon_credits, uncertainty_level)
        
        # For high uncertainty, credits should be reduced
        assert adjusted_credits < carbon_credits

# Test the standalone functions
def test_calculate_biomass_function():
    """Test the standalone biomass calculation function"""
    area_ha = 1000
    forest_type = 'TROPICAL_EVERGREEN'
    canopy_density = 0.8
    
    # Assuming biomass factor for TROPICAL_EVERGREEN is 250
    expected_biomass = 1000 * 250 * 0.8
    
    biomass = calculate_biomass(area_ha, forest_type, canopy_density)
    
    # Check value
    assert abs(biomass - expected_biomass) < 1e-6

def test_calculate_carbon_stock_function():
    """Test the standalone carbon stock calculation function"""
    biomass = 200000  # 200,000 tons
    carbon_fraction = 0.47
    
    expected_carbon_stock = biomass * carbon_fraction
    
    carbon_stock = calculate_carbon_stock(biomass, carbon_fraction)
    
    # Check value
    assert abs(carbon_stock - expected_carbon_stock) < 1e-6

def test_calculate_carbon_credits_function():
    """Test the standalone carbon credits calculation function"""
    carbon_stock = 94000  # 94,000 tons
    co2_equivalent_factor = 3.67
    
    expected_carbon_credits = carbon_stock * co2_equivalent_factor
    
    carbon_credits = calculate_carbon_credits(carbon_stock, co2_equivalent_factor)
    
    # Check value
    assert abs(carbon_credits - expected_carbon_credits) < 1e-6

def test_apply_uncertainty_factor_function():
    """Test the standalone uncertainty factor function"""
    carbon_credits = 345000  # 345,000 tons
    
    # Test with different uncertainty levels
    high_uncertainty_credits = apply_uncertainty_factor(carbon_credits, 'high')
    medium_uncertainty_credits = apply_uncertainty_factor(carbon_credits, 'medium')
    low_uncertainty_credits = apply_uncertainty_factor(carbon_credits, 'low')
    
    # Check that uncertainty reduces credits appropriately
    assert high_uncertainty_credits < medium_uncertainty_credits < low_uncertainty_credits < carbon_credits
