# Image Processing and Color Detection Module

## Overview

The Image Processing and Color Detection Module serves as the foundation of the Forest Carbon Credit Estimation Tool, responsible for analyzing satellite imagery and drone data to accurately identify and classify forest areas using color-based techniques. This module leverages the HSV color space for superior vegetation detection in Vietnamese forest ecosystems.

## Functional Requirements

### Primary Functions
1. **Image Preprocessing**: Enhance image quality and prepare for analysis
2. **Forest Detection**: Identify forest areas using color thresholds
3. **Forest Type Classification**: Differentiate between forest ecosystem types
4. **Area Calculation**: Convert pixel-based detection to geographic areas
5. **Data Export**: Generate vector outputs for downstream processing

### Performance Requirements
- Process images up to 10,000 x 10,000 pixels
- Complete processing in under 30 seconds per km²
- Achieve 90% accuracy in forest area detection
- Support multiple satellite imagery formats (GeoTIFF, JPEG2000, etc.)
- Handle seasonal variation in forest canopy appearance

## Technical Design

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Image Processing Module                  │
│                                                         │
│  ┌───────────────┐   ┌───────────────┐  ┌────────────┐  │
│  │    Image      │   │    Color      │  │  Forest    │  │
│  │ Preprocessor  │──▶│   Detector    │─▶│ Classifier │  │
│  └───────────────┘   └───────────────┘  └────────────┘  │
│          │                   │                │         │
│          ▼                   ▼                ▼         │
│  ┌───────────────┐   ┌───────────────┐  ┌────────────┐  │
│  │   Metadata    │   │     Area      │  │  Result    │  │
│  │   Extractor   │   │  Calculator   │  │ Exporter   │  │
│  └───────────────┘   └───────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Subcomponents

#### 1. Image Preprocessor
- **Input Validation**: Verify image format, resolution, and geospatial metadata
- **Radiometric Correction**: Apply atmospheric and sensor corrections
- **Cloud Masking**: Identify and exclude cloud-covered areas
- **Image Enhancement**: Improve contrast and reduce noise
- **Georeferencing**: Ensure proper spatial alignment

#### 2. Color Detector
- **HSV Conversion**: Transform RGB imagery to HSV color space
- **Threshold Application**: Apply optimized thresholds for Vietnamese forests
- **Noise Reduction**: Remove isolated pixels and small clusters
- **Mask Generation**: Create binary masks of forest/non-forest areas

#### 3. Forest Classifier
- **Spectral Analysis**: Analyze color patterns for forest type determination
- **Forest Type Identification**: Classify into tropical evergreen, deciduous, mangrove, bamboo
- **Confidence Scoring**: Calculate classification confidence metrics
- **Refinement**: Apply post-classification refinement algorithms

#### 4. Metadata Extractor
- **Coordinate System Detection**: Identify spatial reference system
- **Image Resolution Analysis**: Calculate ground sampling distance
- **Acquisition Date Extraction**: Record imagery capture date
- **Sensor Metadata Management**: Store relevant sensor parameters

#### 5. Area Calculator
- **Pixel Counting**: Count forest-classified pixels
- **Scale Factor Application**: Apply spatial resolution conversion
- **Coordinate Transformation**: Convert between different coordinate systems
- **Area Computation**: Calculate forest area in hectares

#### 6. Result Exporter
- **Vector Conversion**: Convert raster results to vector polygons
- **GeoJSON Generation**: Create standardized GeoJSON outputs
- **Shapefile Export**: Produce shapefiles for GIS compatibility
- **Metadata Attachment**: Include processing parameters in outputs

## Detailed Algorithms

### Forest Detection Algorithm

```python
def detect_forest(image_path):
    """
    Detect forest areas in satellite imagery using HSV color space analysis.
    
    Args:
        image_path (str): Path to the satellite image file
        
    Returns:
        tuple: (forest_mask, area_hectares, confidence_score)
    """
    # Load image with geospatial metadata
    with rasterio.open(image_path) as src:
        image = src.read()
        metadata = src.meta
        transform = src.transform
    
    # Convert to BGR for OpenCV
    image_bgr = cv2.merge([image[2], image[1], image[0]])
    
    # Convert BGR to HSV color space
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    
    # Apply optimized HSV thresholds for Vietnamese forests
    # Values calibrated for different forest types
    lower_bound = np.array([30, 40, 40])   # Lower HSV threshold
    upper_bound = np.array([80, 255, 255]) # Upper HSV threshold
    
    # Create binary mask of forest areas
    forest_mask = cv2.inRange(image_hsv, lower_bound, upper_bound)
    
    # Apply morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_OPEN, kernel)
    forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_CLOSE, kernel)
    
    # Count pixels and calculate area
    forest_pixel_count = np.count_nonzero(forest_mask)
    pixel_area_m2 = abs(transform[0] * transform[4])  # Area of one pixel in m²
    area_hectares = (forest_pixel_count * pixel_area_m2) / 10000  # Convert to hectares
    
    # Calculate confidence score based on clarity of classification
    # Higher score indicates more definitive classification
    confidence_score = calculate_confidence(image_hsv, forest_mask)
    
    return forest_mask, area_hectares, confidence_score
```

### Forest Type Classification Algorithm

```python
def classify_forest_type(image_hsv, forest_mask):
    """
    Classify detected forest areas into different forest types.
    
    Args:
        image_hsv (numpy.ndarray): HSV image
        forest_mask (numpy.ndarray): Binary mask of forest areas
        
    Returns:
        dict: Dictionary of forest types with their respective areas
    """
    # Apply mask to original HSV image
    masked_hsv = cv2.bitwise_and(image_hsv, image_hsv, mask=forest_mask)
    
    # HSV ranges for different forest types in Vietnam
    # These ranges are based on calibration with ground truth data
    forest_types = {
        'tropical_evergreen': {
            'lower': np.array([35, 60, 60]),
            'upper': np.array([70, 255, 255])
        },
        'deciduous': {
            'lower': np.array([20, 40, 60]),
            'upper': np.array([35, 220, 220])
        },
        'mangrove': {
            'lower': np.array([40, 50, 30]),
            'upper': np.array([65, 200, 180])
        },
        'bamboo': {
            'lower': np.array([25, 50, 70]),
            'upper': np.array([45, 230, 230])
        }
    }
    
    results = {}
    
    # Classify each forest type
    for forest_type, thresholds in forest_types.items():
        type_mask = cv2.inRange(masked_hsv, thresholds['lower'], thresholds['upper'])
        
        # Apply refinement to reduce misclassification
        type_mask = refine_classification(type_mask)
        
        # Calculate area for this forest type
        type_pixel_count = np.count_nonzero(type_mask)
        type_area_hectares = (type_pixel_count * pixel_area_m2) / 10000
        
        # Store results
        results[forest_type] = {
            'mask': type_mask,
            'area_hectares': type_area_hectares,
            'percentage': (type_pixel_count / forest_pixel_count) * 100 if forest_pixel_count > 0 else 0
        }
    
    return results
```

### HSV Parameter Optimization for Vietnamese Forests

The HSV color space parameters have been optimized for Vietnamese forest ecosystems through extensive calibration with ground truth data. The following table provides the recommended parameter ranges:

| Forest Type | H Range | S Range | V Range |
|-------------|---------|---------|---------|
| Tropical Evergreen | 35-70 | 60-255 | 60-255 |
| Deciduous | 20-35 | 40-220 | 60-220 |
| Mangrove | 40-65 | 50-200 | 30-180 |
| Bamboo | 25-45 | 50-230 | 70-230 |

These parameters should be adjusted seasonally to account for variations in canopy appearance:

- **Dry Season**: Decrease saturation thresholds by 10-15%
- **Rainy Season**: Increase value thresholds by 5-10%
- **Transition Periods**: Widen hue ranges by ±5 points

## Input Requirements

### Supported Image Formats
- GeoTIFF (.tif, .tiff)
- JPEG2000 (.jp2)
- ERDAS Imagine (.img)
- NITF (.nitf)
- ENVI (.bsq, .bil, .bip)

### Metadata Requirements
- Coordinate Reference System (CRS) information
- Acquisition date and time
- Sensor type and resolution
- Preprocessing level information
- Cloud cover percentage

### Resolution Requirements
- **Minimum**: 10 meters per pixel
- **Recommended**: 1-5 meters per pixel
- **Maximum Processing Size**: 30,000 x 30,000 pixels

## Output Specifications

### Vector Data
- **GeoJSON**: Forest polygons with type classification
- **Shapefile**: ESRI-compatible shapefile with attributes
- **KML/KMZ**: Google Earth compatible format

### Raster Data
- **Classified Raster**: GeoTIFF with forest type classification
- **Confidence Raster**: GeoTIFF with classification confidence scores

### Metadata
- **Processing Parameters**: JSON file with all processing settings
- **Area Summary**: CSV file with area calculations by forest type
- **Quality Metrics**: Confidence scores and validation statistics

## Error Handling

### Common Error Scenarios
1. **Invalid Image Format**: System will reject unsupported formats
2. **Missing Geospatial Metadata**: Will prompt for manual coordinate system input
3. **Cloud Cover Threshold Exceeded**: Will flag areas with excessive cloud cover
4. **Insufficient Resolution**: Will warn if resolution is below minimum requirements
5. **Processing Failures**: Will implement graceful degradation with partial results

### Error Response Strategy
- Log detailed error information
- Return meaningful error codes and messages
- Provide recommendations for error resolution
- Support partial processing when possible

## Performance Optimization

### Computational Optimization
- **Parallel Processing**: Implement tile-based parallel processing
- **GPU Acceleration**: Utilize OpenCV's CUDA support where available
- **Memory Management**: Implement streaming processing for large images
- **Algorithm Efficiency**: Optimize computational hot spots

### Resource Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended for large images
- **GPU**: Optional but beneficial for processing acceleration
- **Storage**: SSD recommended for temporary processing files

## Testing and Validation

### Unit Testing
- Each algorithm component has dedicated unit tests
- Mock data inputs for consistent test execution
- Parameterized tests for different forest types

### Integration Testing
- End-to-end testing with sample satellite imagery
- Cross-validation with multiple data sources
- Performance benchmarking under varying loads

### Validation Methodology
- Comparison with manual forest delineation
- Ground truth validation using field survey data
- Cross-comparison with established forest inventories

## Implementation Guidelines

### Development Standards
- Follow PEP 8 style guide for Python code
- Document all functions with docstrings
- Implement type hints for better code clarity
- Maintain 90%+ test coverage

### Dependencies
- OpenCV 4.5+
- NumPy 1.20+
- Rasterio 1.2+
- GDAL 3.3+
- Shapely 1.8+
- GeoPandas 0.10+

### Integration Points
- **Input**: Image Management Service
- **Output**: Geospatial Processing Service
- **Configuration**: Parameter Management Service
- **Logging**: Centralized Logging Service

## Future Enhancements

### Planned Improvements
1. **Deep Learning Integration**: CNN-based forest classification
2. **Temporal Analysis**: Multi-date image analysis for change detection
3. **Hyperspectral Support**: Enhanced classification with additional bands
4. **Automated Calibration**: Self-tuning parameters based on validation data

### Research Areas
1. **Seasonal Variation Modeling**: Adaptive algorithms for seasonal changes
2. **Species Identification**: Finer classification to tree species level
3. **Health Assessment**: Forest health indicators from spectral signatures

## Appendix: Code Examples

### Complete Image Processing Pipeline

```python
def process_satellite_image(image_path, output_dir, parameters=None):
    """
    Complete pipeline for processing satellite imagery for forest carbon estimation.
    
    Args:
        image_path (str): Path to input satellite image
        output_dir (str): Directory for output files
        parameters (dict, optional): Custom processing parameters
    
    Returns:
        dict: Results including areas, confidence scores, and output file paths
    """
    # Initialize default parameters if not provided
    if parameters is None:
        parameters = get_default_parameters()
    
    # 1. Load and preprocess image
    preprocessed_image, metadata = preprocess_image(image_path, parameters)
    
    # 2. Detect forest areas
    forest_mask, forest_area, confidence = detect_forest(preprocessed_image, parameters)
    
    # 3. Classify forest types
    forest_types = classify_forest_type(preprocessed_image, forest_mask, parameters)
    
    # 4. Calculate areas
    area_results = calculate_areas(forest_types, metadata, parameters)
    
    # 5. Export results
    output_files = export_results(
        preprocessed_image, 
        forest_mask, 
        forest_types, 
        area_results, 
        metadata, 
        output_dir, 
        parameters
    )
    
    # 6. Generate summary report
    summary = generate_summary(forest_area, forest_types, confidence, output_files)
    
    return summary
```

This detailed documentation provides a comprehensive guide for implementing the Image Processing and Color Detection Module, covering algorithms, technical specifications, and integration guidelines for development teams.