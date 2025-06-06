import logging
import os
from typing import Dict, Any, Tuple
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, mapping
import cv2
from sqlalchemy.orm import Session

from app.models.imagery import Imagery, ImageryStatusEnum
from app.models.forest import ForestTypeEnum
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

# HSV threshold ranges for Vietnamese forest types (from design)
FOREST_TYPE_HSV_THRESHOLDS = {
    ForestTypeEnum.TROPICAL_EVERGREEN: {'lower': np.array([35, 60, 60]), 'upper': np.array([70, 255, 255])},
    ForestTypeEnum.DECIDUOUS: {'lower': np.array([20, 40, 60]), 'upper': np.array([35, 220, 220])},
    ForestTypeEnum.MANGROVE: {'lower': np.array([40, 50, 30]), 'upper': np.array([65, 200, 180])},
    ForestTypeEnum.BAMBOO: {'lower': np.array([25, 50, 70]), 'upper': np.array([45, 230, 230])},
    ForestTypeEnum.OTHER: {'lower': np.array([30, 40, 40]), 'upper': np.array([80, 255, 255])}
}

# Seasonal adjustment factors for HSV thresholds (from design)
SEASONAL_ADJUSTMENTS = {
    'dry': {'saturation_factor': 0.85, 'value_factor': 1.0},
    'rainy': {'saturation_factor': 1.0, 'value_factor': 1.1},
    'transition': {'hue_range_expansion': 5}
}

class ImageProcessor:
    """
    Refactored processor to align with the detailed design document.
    Handles the image processing workflow with distinct, logical components.
    """
    def __init__(self, imagery_record: Imagery, db_session: Session):
        self.imagery = imagery_record
        self.db = db_session
        self.results: Dict[str, Any] = {}

    def process(self) -> bool:
        """Main method to run the full image processing pipeline."""
        try:
            self._update_status(ImageryStatusEnum.VALIDATING, "Starting validation...")
            self._validate()

            self._update_status(ImageryStatusEnum.PREPROCESSING, "Starting preprocessing...")
            preprocessed_data, profile = self._preprocess()

            season = self._get_season()
            
            self._update_status(ImageryStatusEnum.PREPROCESSING, f"Detecting forest areas for {season} season...")
            forest_mask = self._detect_forest_areas(preprocessed_data, season)
            
            self._update_status(ImageryStatusEnum.PREPROCESSING, "Classifying forest types...")
            classified_raster, class_map = self._classify_forest_types(preprocessed_data, forest_mask, season, profile)
            
            self._update_status(ImageryStatusEnum.PREPROCESSING, "Exporting results...")
            geojson_results = self._export_to_geojson(classified_raster, profile, class_map)

            # Store results (e.g., save to a file, update DB)
            # For now, we'll just log and update status
            # In a real scenario, this would save the geojson, classified raster, etc.
            self.results['classification_geojson'] = geojson_results
            self.results['class_map'] = class_map
            log_message = f"Processing complete. Found {len(geojson_results['features'])} forest polygons."
            logger.info(log_message)
            self._update_status(ImageryStatusEnum.READY, log_message)
            
            return True

        except Exception as e:
            error_message = f"Image processing failed: {str(e)}"
            logger.error(error_message, exc_info=True)
            self._update_status(ImageryStatusEnum.ERROR, error_message)
            return False

    def _update_status(self, status: ImageryStatusEnum, log_message: str):
        """Updates the status of the imagery record in the database."""
        self.imagery.status = status
        self.imagery.processing_log = f"{self.imagery.processing_log or ''}\n{log_message}"
        self.db.add(self.imagery)
        self.db.commit()
        self.db.refresh(self.imagery)
        logger.info(f"Imagery ID {self.imagery.imagery_id}: Status changed to {status}. Message: {log_message}")

    def _get_season(self) -> str:
        """Determines the season based on the image acquisition date for Vietnam."""
        month = self.imagery.acquisition_date.month
        # Approximate seasons for Vietnam
        if 5 <= month <= 10:
            return 'rainy'
        elif 11 <= month or month <= 4:
            return 'dry'
        return 'transition' # Should not happen with current logic

    def _validate(self):
        """Validates the imagery file."""
        if not self.imagery.file_path or not os.path.exists(self.imagery.file_path):
            raise FileNotFoundError(f"Imagery file not found at path: {self.imagery.file_path}")
        
        try:
            with rasterio.open(self.imagery.file_path) as src:
                if src.count < 3:
                    raise ValueError("Image must have at least 3 bands (RGB).")
        except rasterio.errors.RasterioIOError as e:
            raise ValueError(f"Invalid or corrupted raster file: {e}")

    def _preprocess(self) -> Tuple[np.ndarray, Dict]:
        """Loads the image, converts to RGB if needed, and then to HSV."""
        with rasterio.open(self.imagery.file_path) as src:
            # Assuming first 3 bands are R, G, B
            # This might need adjustment based on specific sensor data (e.g., Landsat, Sentinel)
            image_data = src.read([1, 2, 3])
            profile = src.profile

            # Rasterio reads as (bands, height, width), OpenCV needs (height, width, bands)
            image_rgb = np.moveaxis(image_data, 0, -1)
            
            # Normalize to 8-bit if not already, as required by cv2.cvtColor
            if image_rgb.dtype != np.uint8:
                 # Check max value to determine scaling factor
                max_val = image_rgb.max()
                if max_val == 0: # Avoid division by zero for empty images
                    pass
                elif max_val <= 1.0: # Float data in range [0, 1]
                    image_rgb = (image_rgb * 255).astype(np.uint8)
                elif max_val > 255: # e.g., 16-bit data
                    image_rgb = (image_rgb / max_val * 255).astype(np.uint8)
                else:
                    image_rgb = image_rgb.astype(np.uint8)

            hsv_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            return hsv_image, profile

    def _detect_forest_areas(self, image_data: np.ndarray, season: str) -> np.ndarray:
        """Detects general forest areas using a broad HSV mask."""
        # Generic "green" mask to identify all potential vegetation
        lower_green = np.array([30, 40, 40])
        upper_green = np.array([90, 255, 255])
        
        forest_mask = cv2.inRange(image_data, lower_green, upper_green)

        # Simple noise reduction
        kernel = np.ones((5, 5), np.uint8)
        forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_OPEN, kernel)
        forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_CLOSE, kernel)
        
        return forest_mask

    def _classify_forest_types(self, image_data: np.ndarray, forest_mask: np.ndarray, season: str, profile: Dict) -> Tuple[np.ndarray, Dict]:
        """Classifies forest areas into specific types based on HSV thresholds."""
        classified_raster = np.zeros(image_data.shape[:2], dtype=np.uint8)
        class_map = {0: 'Non-Forest'}

        # Assign integer codes to forest types for the raster
        type_to_code = {type_enum: i + 1 for i, type_enum in enumerate(FOREST_TYPE_HSV_THRESHOLDS.keys())}
        for type_enum, code in type_to_code.items():
            class_map[code] = type_enum.value

        for forest_type, code in type_to_code.items():
            thresholds = FOREST_TYPE_HSV_THRESHOLDS[forest_type]
            lower = thresholds['lower'].copy()
            upper = thresholds['upper'].copy()

            # Apply seasonal adjustments from the design document
            adjustments = SEASONAL_ADJUSTMENTS.get(season, {})
            if 'saturation_factor' in adjustments:
                lower[1] = int(lower[1] * adjustments['saturation_factor'])
            if 'value_factor' in adjustments:
                # Be careful not to exceed 255
                upper[2] = int(min(255, upper[2] * adjustments['value_factor']))
            if 'hue_range_expansion' in adjustments:
                lower[0] = max(0, lower[0] - adjustments['hue_range_expansion'])
                upper[0] = min(179, upper[0] + adjustments['hue_range_expansion']) # Hue wraps at 180 in OpenCV

            # Create mask for this specific forest type
            type_mask = cv2.inRange(image_data, lower, upper)
            
            # Apply this mask only where general forest was detected
            final_mask = cv2.bitwise_and(type_mask, type_mask, mask=forest_mask)

            # Assign the class code to the classified raster
            # We do this in reverse order of specificity or based on some priority
            # For now, we assume non-overlapping or let the last one win.
            classified_raster[final_mask > 0] = code
        
        # Save the classified raster for debugging or as a final product
        output_path = self.imagery.file_path.replace('.tif', '_classified.tif')
        profile.update(dtype=rasterio.uint8, count=1, compress='lzw', nodata=0)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(classified_raster, 1)

        self.results['classified_raster_path'] = output_path
        
        return classified_raster, class_map

    def _export_to_geojson(self, classified_raster: np.ndarray, profile: Dict, class_map: Dict) -> Dict:
        """Converts the classified raster into GeoJSON polygons for each class."""
        
        features = []
        # Use a mask to only extract shapes from classified areas (value > 0)
        mask = classified_raster > 0
        
        # The shapes function returns a generator of (geometry, value) tuples
        shape_gen = shapes(
            classified_raster,
            mask=mask,
            transform=profile['transform']
        )
        
        for geom, value in shape_gen:
            class_code = int(value)
            forest_type = class_map.get(class_code, "Unknown")
            
            feature = {
                'type': 'Feature',
                'geometry': mapping(shape(geom)),
                'properties': {
                    'class_code': class_code,
                    'forest_type': forest_type
                }
            }
            features.append(feature)

        return {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {'name': profile['crs'].to_string()}
            },
            'features': features
        }

print("Image processing module loaded with fully refactored ImageProcessor class.")
