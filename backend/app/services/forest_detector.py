import cv2
import numpy as np
from typing import Dict, Any
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ForestAreaDetector:
    """
    A service to detect forest area in an image using color-based segmentation.
    """
    def __init__(self, image_path: str):
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError("Image could not be loaded. Check the path.")
        self.hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

    def detect_forest_area(self) -> float:
        """
        Detects the forest area by filtering for green-like colors.
        Returns the percentage of the image that is detected as forest.
        """
        # Define a range for green color in HSV
        # These values may need tuning depending on the satellite imagery provider
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Create a mask for the green color
        mask = cv2.inRange(self.hsv_image, lower_green, upper_green)

        # Calculate the percentage of green pixels
        total_pixels = self.image.shape[0] * self.image.shape[1]
        green_pixels = cv2.countNonZero(mask)

        if total_pixels == 0:
            return 0.0

        forest_percentage = (green_pixels / total_pixels)
        return forest_percentage

    def get_forest_mask(self):
        """
        Returns the binary mask of the detected forest area.
        """
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(self.hsv_image, lower_green, upper_green)
        return mask

    # Configuration presets for different ecosystem types
    ECOSYSTEM_COLOR_RANGES = {
        'tropical_forest': {
            'lower_hsv': (36, 25, 25),
            'upper_hsv': (70, 255, 255),
            'description': 'Tropical evergreen forests'
        },
        'mangrove': {
            'lower_hsv': (36, 40, 40),
            'upper_hsv': (70, 255, 230),
            'description': 'Mangrove ecosystems (Can Gio specific)'
        },
        'bamboo': {
            'lower_hsv': (25, 20, 50),
            'upper_hsv': (40, 255, 255),
            'description': 'Bamboo forests'
        },
        'plantation': {
            'lower_hsv': (35, 30, 30),
            'upper_hsv': (65, 255, 255),
            'description': 'Plantation forests'
        }
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize detector with optional configuration file
        """
        self.config = self.ECOSYSTEM_COLOR_RANGES.copy()
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                self.config.update(custom_config)
                
        logging.info(f"Initialized ForestAreaDetector with {len(self.config)} ecosystem types")
    
    def detect_area(self, image_path: str, ecosystem_type: str, scale_factor: float) -> Dict[str, Any]:
        """
        Calculate forest area based on specified ecosystem type and scale factor
        
        Parameters:
        - image_path: Path to satellite/drone image
        - ecosystem_type: Type of ecosystem ('tropical_forest', 'mangrove', etc.)
        - scale_factor: Conversion factor from pixels to square meters

        Returns:
        - Dictionary with area metrics and validation data
        """
        if ecosystem_type not in self.config:
            raise ValueError(f"Unknown ecosystem type: {ecosystem_type}. Available types: {list(self.config.keys())}")
        
        try:
            # Read and validate image
            img = cv2.imread(image_path)
            if img is None:
                raise FileNotFoundError(f"Image not found or invalid at {image_path}")
            
            # Image preprocessing for better detection
            img = self._preprocess_image(img)
            
            # Get color range for specified ecosystem
            color_config = self.config[ecosystem_type]
            lower_hsv = np.array(color_config['lower_hsv'])
            upper_hsv = np.array(color_config['upper_hsv'])
            
            # Convert to HSV color space
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Create mask with safety margins
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
            
            # Apply morphological operations to reduce noise
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=2)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            # Calculate pixel area
            colored_pixels = cv2.countNonZero(mask)
            area_m2 = colored_pixels * (scale_factor ** 2)
            area_ha = area_m2 / 10000  # Convert to hectares
            
            # Generate visualization for validation
            # For now, we'll skip returning the actual image data to avoid large responses
            # visualization = self._create_visualization(img, mask)

            # Calculate confidence based on color histogram analysis
            confidence = self._calculate_confidence(hsv, mask)
            
            # Generate validation metrics
            validation = {
                'input_resolution': img.shape[:2],
                'pixel_scale': scale_factor,
                'detection_confidence': confidence,
                'visualization_available': False # Set to false as we are not returning it
            }
            
            logging.info(f"Successfully calculated area for {ecosystem_type}: {area_ha:.2f} hectares")
            
            return {
                'area_m2': float(area_m2),
                'area_ha': float(area_ha),
                'ecosystem_type': ecosystem_type,
                'validation_data': validation,
                # 'visualization': visualization # Not returning raw image data
            }
            
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            raise
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Apply preprocessing to enhance detection quality"""
        # Reduce noise with Gaussian blur
        img = cv2.GaussianBlur(img, (5, 5), 0)
        
        # Enhance contrast with CLAHE
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_img
    
    def _create_visualization(self, img: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Create visualization of detected areas for validation"""
        # Create colored mask for visualization
        color_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        color_mask[:, :, 0] = 0
        color_mask[:, :, 1] = mask
        color_mask[:, :, 2] = 0
        
        # Overlay mask on original image
        alpha = 0.4
        visualization = cv2.addWeighted(img, 1, color_mask, alpha, 0)
        
        # Add contours for better visualization
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(visualization, contours, -1, (0, 255, 0), 2)
        
        return visualization
    
    def _calculate_confidence(self, hsv: np.ndarray, mask: np.ndarray) -> float:
        """Calculate detection confidence based on color distribution"""
        if cv2.countNonZero(mask) == 0:
            return 0.0

        # Calculate histogram of hue channel in detected areas
        hue_channel = hsv[:, :, 0]
        hist = cv2.calcHist([hue_channel], [0], mask, [180], [0, 180])
        
        # Normalize histogram
        hist = cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        
        # Calculate confidence based on peak concentration
        peak_value = np.max(hist)
        peak_index = np.argmax(hist)
        
        # Higher confidence if peak is strong and in green range
        if 30 <= peak_index <= 70 and peak_value > 0.5:
            confidence = peak_value * 0.9
        else:
            confidence = peak_value * 0.6
        
        return float(confidence)

# Example usage (for testing or demonstration)
if __name__ == '__main__':
    # You would need a sample image file named 'satellite_image.jpg'
    # in the same directory to run this example.
    try:
        detector = ForestAreaDetector('satellite_image.jpg')
        percentage = detector.detect_forest_area()
        print(f"Detected forest area: {percentage:.2%}")
        
        # To visualize the result
        forest_mask = detector.get_forest_mask()
        cv2.imshow('Original Image', detector.image)
        cv2.imshow('Forest Mask', forest_mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"You need a sample image 'satellite_image.jpg' to run this example: {e}") 