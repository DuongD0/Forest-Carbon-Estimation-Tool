# Geospatial Processing Module

## Overview

The Geospatial Processing Module is responsible for all spatial data operations within the Forest Carbon Credit Estimation Tool. It handles coordinate system transformations, area calculations, spatial analysis, and integration with standard GIS formats. This module ensures accurate geographic referencing and spatial measurements that are critical for reliable carbon credit estimation.

## Functional Requirements

### Primary Functions
1. **Coordinate System Management**: Handle various coordinate reference systems
2. **Area Calculation**: Compute accurate areas regardless of projection distortion
3. **Spatial Analysis**: Perform vector and raster-based spatial operations
4. **Format Conversion**: Transform between different geospatial data formats
5. **Topology Validation**: Ensure geometric validity of spatial features
6. **Spatial Indexing**: Optimize spatial queries for large datasets

### Performance Requirements
- Support for global and Vietnam-specific coordinate systems
- Area calculation accuracy within 1% of actual area
- Processing of vector datasets with up to 1 million features
- Raster processing of datasets up to 10GB in size
- Query response times under 2 seconds for typical operations

## Technical Design

### Component Architecture

```
┌───────────────────────────────────────────────────────────┐
│               Geospatial Processing Module                 │
│                                                           │
│  ┌─────────────────┐   ┌─────────────────┐  ┌───────────┐ │
│  │  Coordinate     │   │     Spatial     │  │ Format    │ │
│  │  Transformer    │──▶│     Processor   │─▶│ Converter │ │
│  └─────────────────┘   └─────────────────┘  └───────────┘ │
│          │                     │                 │        │
│          ▼                     ▼                 ▼        │
│  ┌─────────────────┐   ┌─────────────────┐  ┌───────────┐ │
│  │     Area        │   │    Topology     │  │ Spatial   │ │
│  │   Calculator    │   │    Validator    │  │ Indexer   │ │
│  └─────────────────┘   └─────────────────┘  └───────────┘ │
└───────────────────────────────────────────────────────────┘
```

### Subcomponents

#### 1. Coordinate Transformer
- **CRS Registry**: Database of coordinate reference systems
- **Transformation Engine**: Algorithms for coordinate conversions
- **Datum Handling**: Management of different geodetic datums
- **Vietnam-specific Transformations**: Support for VN-2000 system

#### 2. Spatial Processor
- **Vector Operations**: Buffer, intersection, union, difference
- **Raster Analysis**: Zonal statistics, reclassification, focal operations
- **Mixed-mode Processing**: Combined raster and vector operations
- **Batch Processing**: Parallel processing of large datasets

#### 3. Format Converter
- **Vector Formats**: GeoJSON, Shapefile, GML, KML conversion
- **Raster Formats**: GeoTIFF, NetCDF, HDF5, ASCII Grid conversion
- **Database Integration**: PostGIS import/export functionality
- **Web Format Support**: WKT, WKB, MVT for web mapping

#### 4. Area Calculator
- **Ellipsoidal Calculations**: Area computation on reference ellipsoid
- **Equal Area Projections**: Albers and other equal-area projections
- **Unit Conversion**: Support for multiple area units (m², ha, km²)
- **Accuracy Assessment**: Error estimation for area calculations

#### 5. Topology Validator
- **Geometry Validation**: Check for self-intersections, gaps, etc.
- **Topology Correction**: Automated fixing of common topology errors
- **Validation Reporting**: Detailed reports of geometric issues
- **Simplification**: Geometry simplification while preserving topology

#### 6. Spatial Indexer
- **R-tree Implementation**: Efficient spatial indexing structure
- **Query Optimization**: Spatial query planning and execution
- **Cache Management**: Caching of frequent spatial queries
- **Index Maintenance**: Automated updating of spatial indexes

## Detailed Algorithms

### Coordinate Transformation Algorithm

```python
def transform_coordinates(geometry, source_crs, target_crs):
    """
    Transform geometry from source coordinate reference system to target CRS.
    
    Args:
        geometry: Shapely geometry object or coordinates array
        source_crs: Source coordinate reference system (EPSG code or proj string)
        target_crs: Target coordinate reference system (EPSG code or proj string)
        
    Returns:
        Transformed geometry in target CRS
    """
    # Initialize transformer
    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS(source_crs), 
        pyproj.CRS(target_crs), 
        always_xy=True
    )
    
    # Apply transformation using Shapely's transform function
    transformed_geometry = shapely.ops.transform(
        transformer.transform, 
        geometry
    )
    
    return transformed_geometry
```

### Area Calculation Algorithm

```python
def calculate_accurate_area(geometry, crs):
    """
    Calculate accurate area for a geometry using appropriate projections.
    
    Args:
        geometry: Shapely geometry object
        crs: Current coordinate reference system of the geometry
        
    Returns:
        area_hectares: Area in hectares
        area_km2: Area in square kilometers
    """
    # Check if CRS is already a projected CRS with equal-area property
    crs_obj = pyproj.CRS(crs)
    
    if not crs_obj.is_projected:
        # For geographic CRS, transform to appropriate equal-area projection
        # For Vietnam, Albers Equal Area is appropriate
        target_crs = pyproj.CRS(
            "+proj=aea +lat_1=8 +lat_2=23 +lat_0=15.5 +lon_0=106 +x_0=0 +y_0=0 "
            "+ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        )
        geometry = transform_coordinates(geometry, crs, target_crs)
    elif not crs_obj.is_equal_area:
        # If projected but not equal-area, transform to an equal-area projection
        target_crs = get_equal_area_crs_for_region(crs_obj)
        geometry = transform_coordinates(geometry, crs, target_crs)
    
    # Calculate area in square meters
    area_m2 = geometry.area
    
    # Convert to hectares and square kilometers
    area_hectares = area_m2 / 10000
    area_km2 = area_m2 / 1000000
    
    return area_hectares, area_km2
```

### Spatial Analysis: Forest Fragmentation Algorithm

```python
def analyze_forest_fragmentation(forest_polygons, buffer_distance=100):
    """
    Analyze forest fragmentation to assess ecosystem integrity.
    
    Args:
        forest_polygons: GeoDataFrame containing forest polygons
        buffer_distance: Distance in meters for connectivity analysis
        
    Returns:
        GeoDataFrame with fragmentation metrics
    """
    # Create a copy to avoid modifying the original
    result = forest_polygons.copy()
    
    # Calculate area and perimeter for each polygon
    result['area_ha'] = result.geometry.area / 10000
    result['perimeter_m'] = result.geometry.length
    
    # Calculate shape index (measure of complexity)
    # Shape index = P / (2 * sqrt(π * A))
    # where P is perimeter and A is area
    result['shape_index'] = result['perimeter_m'] / (2 * np.sqrt(np.pi * result['area_ha'] * 10000))
    
    # Calculate nearest neighbor distance
    spatial_index = result.sindex
    
    def nearest_neighbor_distance(geom):
        possible_matches_idx = list(spatial_index.nearest(geom.bounds, 2))
        if len(possible_matches_idx) > 1:
            possible_matches = result.iloc[possible_matches_idx]
            # Filter out self
            possible_matches = possible_matches[~possible_matches.geometry.equals(geom)]
            if len(possible_matches) > 0:
                return possible_matches.geometry.distance(geom).min()
        return None
    
    result['nn_distance'] = result.geometry.apply(nearest_neighbor_distance)
    
    # Analyze connectivity using buffer method
    buffered = result.copy()
    buffered.geometry = result.geometry.buffer(buffer_distance)
    dissolved = buffered.dissolve()
    
    # Count number of polygons in each connected component
    connected_components = gpd.overlay(result, dissolved, how='intersection')
    connected_components = connected_components.dissolve(by='index_right')
    connected_components['patch_count'] = connected_components.geometry.apply(
        lambda g: len(g) if hasattr(g, '__len__') else 1
    )
    
    # Join back to original data
    result = result.join(
        connected_components['patch_count'].rename('connected_patches'),
        how='left'
    )
    
    # Classify fragmentation level
    def classify_fragmentation(row):
        if row['area_ha'] < 10:
            size_class = 'small'
        elif row['area_ha'] < 100:
            size_class = 'medium'
        else:
            size_class = 'large'
            
        if row['connected_patches'] == 1:
            connectivity = 'isolated'
        elif row['connected_patches'] < 5:
            connectivity = 'poorly_connected'
        else:
            connectivity = 'well_connected'
            
        return f"{size_class}_{connectivity}"
    
    result['fragmentation_class'] = result.apply(classify_fragmentation, axis=1)
    
    return result
```

## Coordinate Systems for Vietnam

### Common Coordinate Systems

| Name | EPSG Code | Description | Use Case |
|------|-----------|-------------|----------|
| VN-2000 | EPSG:9210 | Vietnam's official CRS | Official mapping |
| WGS 84 | EPSG:4326 | Global geographic CRS | GPS, web mapping |
| UTM Zone 48N | EPSG:32648 | UTM for central Vietnam | Project work |
| UTM Zone 49N | EPSG:32649 | UTM for eastern Vietnam | Project work |
| Albers Equal Area | Custom | Equal area projection for Vietnam | Area calculation |

### VN-2000 Parameters

```
+proj=tmerc +lat_0=0 +lon_0=105.75 +k=0.9999 +x_0=500000 +y_0=0 
+ellps=WGS84 +towgs84=-191.90441429,-39.30318279,-111.45032835,
0.00928836,-0.01975479,0.00427372,0.252906278 +units=m +no_defs
```

### Recommended Projection for Area Calculation

For accurate area calculations, use the Vietnam Albers Equal Area projection:

```
+proj=aea +lat_1=8 +lat_2=23 +lat_0=15.5 +lon_0=106 +x_0=0 +y_0=0 
+ellps=WGS84 +datum=WGS84 +units=m +no_defs
```

## Supported Geospatial Formats

### Vector Formats
- **GeoJSON** (.geojson): Web-friendly format for feature data
- **Shapefile** (.shp, .dbf, .shx, .prj): ESRI's standard format
- **GeoPackage** (.gpkg): OGC standard for vector and raster data
- **KML/KMZ** (.kml, .kmz): Google Earth format
- **GML** (.gml): OGC Geography Markup Language

### Raster Formats
- **GeoTIFF** (.tif, .tiff): Georeferenced TIFF images
- **ERDAS Imagine** (.img): Proprietary raster format
- **NetCDF** (.nc): Scientific data format for multidimensional data
- **ASCII Grid** (.asc): Simple text-based grid format
- **Cloud Optimized GeoTIFF** (.tif): Web-optimized GeoTIFF

### Database Formats
- **PostGIS**: Spatial extension for PostgreSQL
- **GeoPackage** (.gpkg): SQLite-based database for GIS data
- **FileGDB** (.gdb): ESRI's file geodatabase format

## Spatial Operations

### Vector Operations
- **Buffer**: Create zones around features
- **Intersection**: Find common areas between features
- **Union**: Combine features into a single feature
- **Difference**: Subtract one feature from another
- **Dissolve**: Merge features based on attributes
- **Clip**: Cut features using a boundary
- **Simplify**: Reduce vertex count while preserving shape

### Raster Operations
- **Reclassification**: Change cell values based on conditions
- **Zonal Statistics**: Calculate statistics within zones
- **Focal Operations**: Calculate statistics within moving windows
- **Map Algebra**: Perform arithmetic operations between rasters
- **Interpolation**: Create continuous surfaces from point data
- **Extraction**: Extract values at specific locations

### Topology Rules
- **No Gaps**: Ensure no gaps between adjacent polygons
- **No Overlaps**: Ensure no overlap between polygons
- **No Self-Intersections**: Ensure polygons don't intersect themselves
- **No Dangles**: Ensure lines connect properly at endpoints
- **No Duplicates**: Ensure no duplicate features exist

## Error Handling

### Common Error Scenarios
1. **Invalid Geometry**: System will attempt to repair or report detailed error
2. **Transformation Failure**: Will provide specific error for coordinate transformation issues
3. **Format Conversion Errors**: Will detail specific format compliance issues
4. **Out of Bounds Coordinates**: Will validate coordinate ranges
5. **Topology Errors**: Will identify and provide options to fix topology issues

### Error Response Strategy
- Detailed error messages with specific locations of issues
- Automated repair attempts where feasible
- Graceful degradation with partial processing when possible
- Warning system for potential accuracy issues

## Performance Optimization

### Computational Optimization
- **Spatial Indexing**: R-tree implementation for faster spatial queries
- **Parallel Processing**: Multi-threaded processing for large datasets
- **Lazy Loading**: Defer loading large datasets until needed
- **Query Optimization**: Efficient SQL for database operations
- **Simplification**: Appropriate generalization for display purposes

### Resource Requirements
- **CPU**: Multi-core processor recommended for parallel processing
- **RAM**: 16GB minimum for processing large datasets
- **Storage**: SSD recommended for database operations
- **Network**: Fast connection for web service integration

## Testing and Validation

### Unit Testing
- Tests for each spatial operation with known results
- Edge case testing for geometric complexity
- Performance testing for large datasets

### Integration Testing
- End-to-end testing with real-world data
- Cross-validation with established GIS software
- API integration testing

### Validation Methodology
- Comparison with national mapping agency data
- Validation against high-precision survey data
- Cross-comparison with different calculation methods

## Implementation Guidelines

### Development Standards
- Follow PEP 8 style guide for Python code
- Document all functions with docstrings
- Implement type hints for better code clarity
- Use GeoPandas for vector data handling
- Use Rasterio for raster data processing

### Dependencies
- GeoPandas 0.10+
- Rasterio 1.2+
- PyProj 3.0+
- Shapely 1.8+
- Fiona 1.8+
- SQLAlchemy with GeoAlchemy2 (for database operations)

### Integration Points
- **Input**: Image Processing Module
- **Output**: Carbon Calculation Engine
- **Storage**: PostgreSQL/PostGIS Database
- **API**: RESTful Services for web integration

## Code Examples

### Complete Geospatial Processing Pipeline

```python
def process_forest_data(forest_mask_path, metadata, output_dir):
    """
    Complete pipeline for geospatial processing of forest data.
    
    Args:
        forest_mask_path (str): Path to forest mask raster
        metadata (dict): Metadata including coordinate system info
        output_dir (str): Directory for output files
    
    Returns:
        dict: Results including processed files and statistics
    """
    # 1. Load forest mask raster
    with rasterio.open(forest_mask_path) as src:
        forest_mask = src.read(1)
        transform = src.transform
        crs = src.crs
    
    # 2. Convert raster to vector polygons
    forest_polygons = raster_to_vector(forest_mask, transform, crs)
    
    # 3. Clean and validate polygon geometry
    forest_polygons = validate_and_repair_geometry(forest_polygons)
    
    # 4. Transform to appropriate coordinate system for Vietnam
    forest_polygons_projected = reproject_to_vietnam_crs(forest_polygons, crs)
    
    # 5. Calculate accurate areas
    forest_areas = calculate_forest_areas(forest_polygons_projected)
    
    # 6. Perform fragmentation analysis
    fragmentation_results = analyze_forest_fragmentation(forest_polygons_projected)
    
    # 7. Export to various formats
    output_files = export_to_formats(
        forest_polygons_projected,
        fragmentation_results,
        forest_areas,
        output_dir
    )
    
    # 8. Generate summary statistics
    summary_stats = generate_spatial_statistics(
        forest_polygons_projected,
        fragmentation_results
    )
    
    return {
        'output_files': output_files,
        'statistics': summary_stats
    }
```

### Polygon Vectorization Function

```python
def raster_to_vector(raster_data, transform, crs):
    """
    Convert a binary raster mask to vector polygons.
    
    Args:
        raster_data (numpy.ndarray): Binary raster data
        transform (affine.Affine): Affine transformation
        crs: Coordinate reference system
        
    Returns:
        geopandas.GeoDataFrame: Vector polygons
    """
    # Find contours of raster features
    shapes = rasterio.features.shapes(
        raster_data.astype('uint8'),
        mask=(raster_data > 0),
        transform=transform
    )
    
    # Convert shapes to GeoJSON features
    features = [
        {
            'geometry': shape,
            'properties': {'value': value}
        }
        for shape, value in shapes
    ]
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(features, crs=crs)
    
    # Filter out features with value of 0 (background)
    gdf = gdf[gdf.value > 0].copy()
    
    # Simplify geometries slightly to remove pixel stepping
    gdf.geometry = gdf.geometry.simplify(1.0, preserve_topology=True)
    
    return gdf
```

### Coordinate System Transformation Function

```python
def reproject_to_vietnam_crs(gdf, source_crs):
    """
    Reproject data to appropriate coordinate system for Vietnam.
    
    Args:
        gdf (geopandas.GeoDataFrame): Input geodataframe
        source_crs: Source coordinate reference system
        
    Returns:
        geopandas.GeoDataFrame: Reprojected geodataframe
    """
    # Set source CRS if not already set
    if gdf.crs is None:
        gdf.set_crs(source_crs, inplace=True)
    
    # For area calculations, use Vietnam Albers Equal Area
    vietnam_albers = pyproj.CRS(
        "+proj=aea +lat_1=8 +lat_2=23 +lat_0=15.5 +lon_0=106 "
        "+x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    )
    
    # For official mapping, use VN-2000
    vn2000 = pyproj.CRS(
        "+proj=tmerc +lat_0=0 +lon_0=105.75 +k=0.9999 +x_0=500000 +y_0=0 "
        "+ellps=WGS84 +towgs84=-191.90441429,-39.30318279,-111.45032835,"
        "0.00928836,-0.01975479,0.00427372,0.252906278 +units=m +no_defs"
    )
    
    # Reproject to Vietnam Albers for area calculations
    gdf_albers = gdf.to_crs(vietnam_albers)
    
    # Calculate areas in the equal area projection
    gdf_albers['area_ha'] = gdf_albers.geometry.area / 10000
    gdf_albers['area_km2'] = gdf_albers.geometry.area / 1000000
    
    # Also create a version in VN-2000 for official mapping
    gdf_vn2000 = gdf.to_crs(vn2000)
    
    # Transfer calculated areas to VN-2000 version
    gdf_vn2000['area_ha'] = gdf_albers['area_ha']
    gdf_vn2000['area_km2'] = gdf_albers['area_km2']
    
    # Return both versions
    return {
        'equal_area': gdf_albers,  # For analysis
        'official': gdf_vn2000     # For official mapping
    }
```

This detailed documentation provides a comprehensive guide for implementing the Geospatial Processing Module, covering algorithms, coordinate systems, and integration guidelines for development teams.