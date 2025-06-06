import pytest
from unittest.mock import MagicMock, patch
from app.processing.geospatial_processor import (
    GeospatialProcessor,
    reproject_geometry,
    calculate_area,
    buffer_geometry,
    intersect_geometries
)
import numpy as np
import shapely.geometry as shp

# Test the GeospatialProcessor class
class TestGeospatialProcessor:
    
    @pytest.fixture
    def processor(self):
        return GeospatialProcessor()
    
    @pytest.fixture
    def sample_polygon(self):
        # Create a simple square polygon
        return shp.Polygon([
            (0, 0), (0, 10), (10, 10), (10, 0), (0, 0)
        ])
    
    def test_init(self, processor):
        """Test that the GeospatialProcessor initializes correctly"""
        assert processor.default_crs == 'EPSG:4326'
        assert processor.supported_formats == ['GeoJSON', 'WKT', 'Shapefile']
        assert processor.max_vertices == 10000
    
    def test_validate_geometry_valid(self, processor, sample_polygon):
        """Test geometry validation with valid data"""
        # Mock metadata
        metadata = {
            'format': 'GeoJSON',
            'crs': 'EPSG:4326'
        }
        
        result = processor.validate_geometry(sample_polygon, metadata)
        assert result is True
    
    def test_validate_geometry_invalid_format(self, processor, sample_polygon):
        """Test geometry validation with invalid format"""
        # Mock metadata with unsupported format
        metadata = {
            'format': 'KML',
            'crs': 'EPSG:4326'
        }
        
        with pytest.raises(ValueError) as excinfo:
            processor.validate_geometry(sample_polygon, metadata)
        assert "Unsupported geometry format" in str(excinfo.value)
    
    def test_validate_geometry_too_complex(self, processor):
        """Test geometry validation with too many vertices"""
        # Create a complex polygon with too many vertices
        coords = [(float(i), float(i % 100)) for i in range(15000)]
        complex_polygon = shp.Polygon(coords)
        
        metadata = {
            'format': 'GeoJSON',
            'crs': 'EPSG:4326'
        }
        
        with pytest.raises(ValueError) as excinfo:
            processor.validate_geometry(complex_polygon, metadata)
        assert "Geometry too complex" in str(excinfo.value)
    
    @patch('app.processing.geospatial_processor.reproject_geometry')
    def test_process_geometry_area(self, mock_reproject, processor, sample_polygon):
        """Test processing geometry for area calculation"""
        # Setup mock return for reproject_geometry
        mock_reproject.return_value = sample_polygon
        
        # Mock the calculate_area function
        processor.calculate_area = MagicMock(return_value=100.0)
        
        result = processor.process_geometry(sample_polygon, 'area', source_crs='EPSG:4326')
        
        # Verify reproject_geometry was called
        mock_reproject.assert_called_once()
        
        # Verify calculate_area was called
        processor.calculate_area.assert_called_once()
        
        # Check result
        assert result is not None
        assert 'area' in result
        assert result['area'] == 100.0
        assert 'units' in result
        assert result['units'] == 'square_meters'
    
    @patch('app.processing.geospatial_processor.reproject_geometry')
    def test_process_geometry_buffer(self, mock_reproject, processor, sample_polygon):
        """Test processing geometry for buffer operation"""
        # Setup mock return for reproject_geometry
        mock_reproject.return_value = sample_polygon
        
        # Mock the buffer_geometry function
        buffered_polygon = sample_polygon.buffer(10)
        processor.buffer_geometry = MagicMock(return_value=buffered_polygon)
        
        result = processor.process_geometry(sample_polygon, 'buffer', buffer_distance=10)
        
        # Verify reproject_geometry was called
        mock_reproject.assert_called_once()
        
        # Verify buffer_geometry was called
        processor.buffer_geometry.assert_called_once()
        
        # Check result
        assert result is not None
        assert 'geometry' in result
        assert 'buffer_distance' in result
        assert result['buffer_distance'] == 10
    
    def test_calculate_area(self, processor, sample_polygon):
        """Test area calculation"""
        # For a 10x10 square, area should be 100
        expected_area = 100.0
        
        area = processor.calculate_area(sample_polygon)
        
        # Check value (with tolerance for floating point)
        assert abs(area - expected_area) < 1e-6
    
    def test_buffer_geometry(self, processor, sample_polygon):
        """Test geometry buffering"""
        buffer_distance = 5.0
        
        # Buffer the polygon
        buffered = processor.buffer_geometry(sample_polygon, buffer_distance)
        
        # Check that the result is a polygon
        assert isinstance(buffered, shp.Polygon)
        
        # Check that the area has increased
        original_area = sample_polygon.area
        buffered_area = buffered.area
        assert buffered_area > original_area
        
        # For a square with side length 10, buffering by 5 should add approximately
        # 5 units on each side, making it a 20x20 square plus rounded corners
        # Area should be greater than 20*20 = 400
        assert buffered_area > 400
    
    def test_intersect_geometries(self, processor):
        """Test geometry intersection"""
        # Create two overlapping squares
        square1 = shp.Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
        square2 = shp.Polygon([(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)])
        
        # Expected intersection is a 5x5 square
        expected_area = 25.0
        
        intersection = processor.intersect_geometries(square1, square2)
        
        # Check that the result is a polygon
        assert isinstance(intersection, shp.Polygon)
        
        # Check the area of the intersection
        assert abs(intersection.area - expected_area) < 1e-6

# Test the standalone functions
def test_reproject_geometry():
    """Test geometry reprojection function"""
    # Create a test polygon
    polygon = shp.Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
    
    # Mock the reprojection function since actual reprojection requires GDAL/pyproj
    with patch('app.processing.geospatial_processor.pyproj.Transformer.from_crs') as mock_transformer:
        # Setup the mock transformer
        mock_transform = MagicMock()
        mock_transform.transform.side_effect = lambda x, y: (x * 111000, y * 111000)  # Approximate conversion from degrees to meters
        mock_transformer.return_value = mock_transform
        
        # Reproject the geometry
        reprojected = reproject_geometry(polygon, 'EPSG:4326', 'EPSG:3857')
        
        # Check that the transformer was called
        mock_transformer.assert_called_once()
        
        # Check that the result is a polygon
        assert isinstance(reprojected, shp.Polygon)
        
        # Check that the coordinates were transformed
        # Original coordinates in degrees, new ones should be in meters
        assert reprojected.area > polygon.area

def test_calculate_area_function():
    """Test the standalone area calculation function"""
    # Create a test polygon (10x10 square)
    polygon = shp.Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    
    # Expected area is 100 square units
    expected_area = 100.0
    
    area = calculate_area(polygon)
    
    # Check value (with tolerance for floating point)
    assert abs(area - expected_area) < 1e-6

def test_buffer_geometry_function():
    """Test the standalone buffer function"""
    # Create a test polygon (10x10 square)
    polygon = shp.Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    buffer_distance = 5.0
    
    # Buffer the polygon
    buffered = buffer_geometry(polygon, buffer_distance)
    
    # Check that the result is a polygon
    assert isinstance(buffered, shp.Polygon)
    
    # Check that the area has increased
    assert buffered.area > polygon.area

def test_intersect_geometries_function():
    """Test the standalone intersection function"""
    # Create two overlapping squares
    square1 = shp.Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    square2 = shp.Polygon([(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)])
    
    # Expected intersection is a 5x5 square
    expected_area = 25.0
    
    intersection = intersect_geometries(square1, square2)
    
    # Check that the result is a polygon
    assert isinstance(intersection, shp.Polygon)
    
    # Check the area of the intersection
    assert abs(intersection.area - expected_area) < 1e-6
