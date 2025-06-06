# Geospatial Processing Logic

import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from pyproj import CRS, Transformer, Proj
from shapely.ops import transform as shapely_transform
import json
import logging
import math
from typing import Dict, Any, Tuple
from pyproj.exceptions import ProjError

from app.models.forest import Forest
from app.models.imagery import Imagery

# Setup logger
logger = logging.getLogger(__name__)

# Define the VN-2000 projection string as per the design document
VN2000_PROJECTED_CRS = "EPSG:3405" # VN-2000 / UTM zone 48N
VN2000_GEOGRAPHIC_CRS = "EPSG:4756" # VN-2000 Geographic
WGS84_CRS = "EPSG:4326" # WGS 84 Geographic

class GeospatialProcessor:
    """
    Handles advanced geospatial operations, including transformations,
    area calculations, and raster/vector interactions, with a focus on
    Vietnam-specific coordinate systems.
    """

    def __init__(self, source_crs: str = WGS84_CRS):
        self.source_crs = CRS.from_string(source_crs)

    def _get_appropriate_utm_zone(self, geometry: Any) -> CRS:
        """Determines the most appropriate UTM zone for a given geometry."""
        centroid = geometry.centroid
        utm_zone_number = int((centroid.x + 180) / 6) + 1
        is_northern = centroid.y >= 0
        utm_crs = CRS(f"EPSG:326{utm_zone_number if is_northern else 327}{utm_zone_number}")
        return utm_crs

    def _transform_geom(self, geometry: Any, source_crs: CRS, target_crs: CRS) -> Any:
        """Helper function to reproject a shapely geometry."""
        project = Transformer.from_crs(source_crs, target_crs, always_xy=True).transform
        return shapely_transform(project, geometry)

    def calculate_accurate_area(self, geometry_geojson: Dict) -> Dict[str, float]:
        """
        Calculates the area of a geometry by transforming it to a suitable
        local equal-area projection.
        """
        try:
            geom = shape(geometry_geojson)
            # Use a local UTM projection for accurate area measurement
            target_crs = self._get_appropriate_utm_zone(geom)
            
            projected_geom = self._transform_geom(geom, self.source_crs, target_crs)
            
            area_m2 = projected_geom.area
            area_ha = area_m2 / 10000.0
            
            return {"area_sq_meters": area_m2, "area_hectares": area_ha}
        except Exception as e:
            logger.error(f"Failed to calculate area: {e}", exc_info=True)
            raise

    def transform_geometry(self, geometry_geojson: Dict, target_crs_str: str) -> Dict:
        """Transforms a geometry to the specified target CRS (e.g., VN-2000)."""
        try:
            target_crs = CRS.from_string(target_crs_str)
            geom = shape(geometry_geojson)
            
            transformed_geom = self._transform_geom(geom, self.source_crs, target_crs)
            
            return mapping(transformed_geom)
        except ProjError as e:
            logger.error(f"CRS transformation failed: {e}", exc_info=True)
            raise ValueError(f"Invalid target CRS: {target_crs_str}")
        except Exception as e:
            logger.error(f"Failed to transform geometry: {e}", exc_info=True)
            raise

    def clip_raster_to_geometry(self, raster_path: str, geometry_geojson: Dict, output_path: str) -> str:
        """Clips a raster file to the bounds of a vector geometry."""
        if not os.path.exists(raster_path):
            raise FileNotFoundError(f"Raster file not found: {raster_path}")

        geometries = [geometry_geojson]
        
        with rasterio.open(raster_path) as src:
            # Transform geometry to match raster CRS if they don't match
            if CRS.from_string(self.source_crs.to_string()) != CRS.from_string(src.crs.to_string()):
                geom_shape = shape(geometry_geojson)
                transformed_geom = self._transform_geom(geom_shape, self.source_crs, src.crs)
                geometries = [mapping(transformed_geom)]

            out_image, out_transform = mask(src, geometries, crop=True)
            out_meta = src.meta.copy()

        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "compress": "lzw"
        })

        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)
            
        return output_path

    def validate_topology(self, geometry_geojson: Dict) -> Dict[str, Any]:
        """Checks for geometry validity (e.g., self-intersections)."""
        geom = shape(geometry_geojson)
        is_valid = geom.is_valid
        
        response = {"is_valid": is_valid, "reason": None}
        if not is_valid:
            # from shapely.validation import explain_validity
            # response['reason'] = explain_validity(geom) # More detailed reason
            response['reason'] = 'The geometry is invalid (e.g., self-intersection, incorrect ring orientation).'
        return response

    def calculate_fragmentation(self, geometry_geojson: Dict) -> Dict[str, float]:
        """Calculates forest fragmentation metrics for a given forest geometry."""
        gdf = gpd.GeoDataFrame([1], geometry=[shape(geometry_geojson)], crs=self.source_crs)
        
        # Transform to an equal-area projection for accurate area/perimeter calcs
        target_crs = self._get_appropriate_utm_zone(gdf.geometry.iloc[0])
        gdf_proj = gdf.to_crs(target_crs)
        
        area = gdf_proj.geometry.area.iloc[0]
        perimeter = gdf_proj.geometry.length.iloc[0]
        
        if area == 0 or perimeter == 0:
            return {
                "shape_index": 0,
                "fractal_dimension": 0,
                "core_area_index": 0
            }

        # Shape Index: Measures complexity compared to a circle
        shape_index = perimeter / (2 * np.sqrt(np.pi * area))
        
        # Fractal Dimension: Relates perimeter to area
        fractal_dimension = (2 * np.log(perimeter / 4)) / np.log(area)
        
        # Core Area Index (assuming a buffer/edge effect of 100 meters)
        edge_buffer = 100 
        core_area = gdf_proj.geometry.buffer(-edge_buffer).area.iloc[0]
        core_area_index = (core_area / area) if area > 0 else 0
        
        return {
            "shape_index": round(shape_index, 4),
            "fractal_dimension": round(fractal_dimension, 4),
            "core_area_index": round(core_area_index, 4)
        }

print("Geospatial processing module loaded with fully refactored GeospatialProcessor class.")
