import pytest
from unittest.mock import MagicMock, patch
from app.processing.image_processor import (
    ImageProcessor,
    preprocess_image,
    calculate_ndvi,
    segment_forest_area,
    extract_forest_features
)
import numpy as np

# Test the ImageProcessor class
class TestImageProcessor:
    
    @pytest.fixture
    def mock_image_data(self):
        # Create a simple mock image array (10x10 with 4 bands)
        return np.random.randint(0, 255, (10, 10, 4), dtype=np.uint8)
    
    @pytest.fixture
    def processor(self):
        return ImageProcessor()
    
    def test_init(self, processor):
        """Test that the ImageProcessor initializes correctly"""
        assert processor.supported_formats == ['GeoTIFF', 'JPEG', 'PNG']
        assert processor.max_image_size == 10000
        assert processor.default_output_format == 'GeoTIFF'
    
    def test_validate_image_valid(self, processor, mock_image_data):
        """Test image validation with valid data"""
        # Mock metadata
        metadata = {
            'format': 'GeoTIFF',
            'dimensions': (10, 10),
            'bands': 4
        }
        
        result = processor.validate_image(mock_image_data, metadata)
        assert result is True
    
    def test_validate_image_invalid_format(self, processor, mock_image_data):
        """Test image validation with invalid format"""
        # Mock metadata with unsupported format
        metadata = {
            'format': 'BMP',
            'dimensions': (10, 10),
            'bands': 4
        }
        
        with pytest.raises(ValueError) as excinfo:
            processor.validate_image(mock_image_data, metadata)
        assert "Unsupported image format" in str(excinfo.value)
    
    def test_validate_image_too_large(self, processor, mock_image_data):
        """Test image validation with image too large"""
        # Mock metadata with dimensions too large
        metadata = {
            'format': 'GeoTIFF',
            'dimensions': (20000, 20000),
            'bands': 4
        }
        
        with pytest.raises(ValueError) as excinfo:
            processor.validate_image(mock_image_data, metadata)
        assert "Image dimensions exceed maximum allowed" in str(excinfo.value)
    
    @patch('app.processing.image_processor.preprocess_image')
    def test_process_image_ndvi(self, mock_preprocess, processor, mock_image_data):
        """Test processing image for NDVI calculation"""
        # Setup mock return for preprocess_image
        mock_preprocess.return_value = mock_image_data
        
        # Mock the calculate_ndvi function
        processor.calculate_ndvi = MagicMock(return_value=np.zeros((10, 10)))
        
        result = processor.process_image(mock_image_data, 'ndvi')
        
        # Verify preprocess_image was called
        mock_preprocess.assert_called_once_with(mock_image_data)
        
        # Verify calculate_ndvi was called
        processor.calculate_ndvi.assert_called_once()
        
        # Check result
        assert result is not None
        assert 'ndvi_result' in result
        assert 'metadata' in result
    
    @patch('app.processing.image_processor.preprocess_image')
    def test_process_image_forest_mask(self, mock_preprocess, processor, mock_image_data):
        """Test processing image for forest mask generation"""
        # Setup mock return for preprocess_image
        mock_preprocess.return_value = mock_image_data
        
        # Mock the segment_forest_area function
        processor.segment_forest_area = MagicMock(return_value=np.zeros((10, 10), dtype=bool))
        
        result = processor.process_image(mock_image_data, 'forest_mask')
        
        # Verify preprocess_image was called
        mock_preprocess.assert_called_once_with(mock_image_data)
        
        # Verify segment_forest_area was called
        processor.segment_forest_area.assert_called_once()
        
        # Check result
        assert result is not None
        assert 'forest_mask' in result
        assert 'metadata' in result
    
    def test_calculate_ndvi(self, processor, mock_image_data):
        """Test NDVI calculation"""
        # Create a controlled test image with known NIR and RED values
        test_image = np.zeros((5, 5, 4), dtype=np.float32)
        # Set NIR band (index 3) to 0.8
        test_image[:, :, 3] = 0.8
        # Set RED band (index 2) to 0.4
        test_image[:, :, 2] = 0.4
        
        # Expected NDVI: (NIR - RED) / (NIR + RED) = (0.8 - 0.4) / (0.8 + 0.4) = 0.4 / 1.2 = 0.333...
        expected_ndvi = np.full((5, 5), 0.333333, dtype=np.float32)
        
        ndvi_result = processor.calculate_ndvi(test_image)
        
        # Check shape
        assert ndvi_result.shape == (5, 5)
        
        # Check values (with tolerance for floating point)
        np.testing.assert_allclose(ndvi_result, expected_ndvi, rtol=1e-5)
    
    def test_segment_forest_area(self, processor):
        """Test forest area segmentation"""
        # Create a test NDVI image with known values
        ndvi = np.zeros((5, 5), dtype=np.float32)
        # Set some pixels above the threshold (0.4)
        ndvi[1:4, 1:4] = 0.6
        
        # Expected mask: True where NDVI > threshold
        expected_mask = np.zeros((5, 5), dtype=bool)
        expected_mask[1:4, 1:4] = True
        
        forest_mask = processor.segment_forest_area(ndvi, threshold=0.4)
        
        # Check shape
        assert forest_mask.shape == (5, 5)
        
        # Check values
        np.testing.assert_array_equal(forest_mask, expected_mask)

# Test the standalone functions
def test_preprocess_image():
    """Test image preprocessing function"""
    # Create a test image
    image = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
    
    # Process the image
    processed = preprocess_image(image)
    
    # Check that the output has the same shape
    assert processed.shape == image.shape
    
    # Check that the values are normalized to [0, 1]
    assert np.max(processed) <= 1.0
    assert np.min(processed) >= 0.0

def test_calculate_ndvi_function():
    """Test the standalone NDVI calculation function"""
    # Create a test image with known NIR and RED values
    image = np.zeros((5, 5, 4), dtype=np.float32)
    # Set NIR band (index 3) to 0.8
    image[:, :, 3] = 0.8
    # Set RED band (index 2) to 0.4
    image[:, :, 2] = 0.4
    
    # Expected NDVI: (NIR - RED) / (NIR + RED) = (0.8 - 0.4) / (0.8 + 0.4) = 0.4 / 1.2 = 0.333...
    expected_ndvi = np.full((5, 5), 0.333333, dtype=np.float32)
    
    ndvi_result = calculate_ndvi(image)
    
    # Check shape
    assert ndvi_result.shape == (5, 5)
    
    # Check values (with tolerance for floating point)
    np.testing.assert_allclose(ndvi_result, expected_ndvi, rtol=1e-5)

def test_extract_forest_features():
    """Test forest feature extraction function"""
    # Create a test forest mask
    mask = np.zeros((10, 10), dtype=bool)
    # Create a simple forest patch
    mask[2:8, 2:8] = True
    
    features = extract_forest_features(mask)
    
    # Check that we get the expected features
    assert 'area_pixels' in features
    assert features['area_pixels'] == 36  # 6x6 patch
    assert 'perimeter_pixels' in features
    assert 'compactness' in features
