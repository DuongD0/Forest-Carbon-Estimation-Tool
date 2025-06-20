import cv2
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
import logging
import math
from dataclasses import dataclass
from enum import Enum
import base64
import os

from app.models.ecosystem import Ecosystem

# Import AI detector
try:
    from app.services.ai_forest_detector import ai_forest_detector, AIDetectionResult
    AI_DETECTOR_AVAILABLE = True
    logging.info("AI Forest Detector loaded successfully")
except ImportError as e:
    AI_DETECTOR_AVAILABLE = False
    logging.warning(f"AI Forest Detector not available: {e}. Using traditional methods only.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ImageryType(Enum):
    """Types of imagery based on spectral characteristics"""
    RGB_NATURAL = "rgb_natural"  # Natural color RGB
    FALSE_COLOR = "false_color"  # False color composite (NIR-Red-Green)
    NDVI = "ndvi"  # Normalized Difference Vegetation Index
    MULTISPECTRAL = "multispectral"  # Multi-band imagery
    THERMAL = "thermal"  # Thermal infrared
    SAR = "sar"  # Synthetic Aperture Radar
    LIDAR = "lidar"  # LiDAR data

@dataclass
class ForestRegion:
    """Represents a detected forest region with bounding box"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    area_pixels: int
    area_hectares: float
    confidence: float
    forest_type: str
    density: str  # 'dense', 'medium', 'sparse'
    health_status: str  # 'healthy', 'stressed', 'degraded'
    carbon_density_estimate: float  # tC/ha
    biomass_density_estimate: float  # t/ha

@dataclass
class ColorSpectrumAnalysis:
    """Results of automatic color spectrum analysis"""
    imagery_type: ImageryType
    dominant_colors: List[Tuple[int, int, int]]
    vegetation_indices: Dict[str, float]
    spectral_characteristics: Dict[str, Any]
    recommended_analysis_method: str

@dataclass
class ForestClassification:
    """Data class for forest classification results"""
    forest_type: str
    confidence: float
    carbon_density: float  # tC/ha
    biomass_density: float  # t/ha
    area_ha: float

class AdvancedForestDetector:
    """
    Advanced forest area detector using RGB analysis, vegetation indices,
    and industry-standard methodologies for carbon credit applications.
    
    Features:
    - Automatic color spectrum detection
    - Vietnamese forest specialization
    - Automatic bounding box generation
    - RGB-based forest classification
    - Vegetation index calculations (NDVI approximation, ExG, VARI)
    - Multiple forest type detection with different carbon densities
    - VCS-compliant uncertainty assessment
    - Texture analysis for forest health assessment
    """

    def __init__(self):
        """Initialize the advanced forest detector with industry parameters."""
        logging.info("Initialized AdvancedForestDetector with automatic detection features")
        
        # Vietnamese forest signatures with more inclusive color ranges
        self.vietnamese_forest_signatures = {
            'evergreen_broadleaf': {
                'rgb_ranges': [
                    {'lower': np.array([0, 30, 0]), 'upper': np.array([100, 150, 100])},  # Broader green range
                    {'lower': np.array([10, 40, 10]), 'upper': np.array([90, 140, 90])},  # Dark green
                    {'lower': np.array([20, 50, 20]), 'upper': np.array([110, 160, 110])},  # Medium green
                    {'lower': np.array([30, 60, 30]), 'upper': np.array([120, 180, 120])}   # Light green
                ],
                'ndvi_threshold': 0.3,  # Lowered for better detection
                'texture_features': {'homogeneity': 0.7, 'contrast': 0.3},
                'carbon_density': 120,  # tC/ha
                'biomass_density': 240,  # t/ha
                'description': 'Dense tropical rainforest with high biodiversity'
            },
            'deciduous_dipterocarp': {
                'rgb_ranges': [
                    {'lower': np.array([20, 40, 10]), 'upper': np.array([120, 160, 100])},  # Broader range
                    {'lower': np.array([30, 50, 20]), 'upper': np.array([130, 170, 110])},
                    {'lower': np.array([40, 60, 30]), 'upper': np.array([140, 180, 120])}
                ],
                'ndvi_threshold': 0.25,  # Lower for dry deciduous
                'texture_features': {'homogeneity': 0.6, 'contrast': 0.4},
                'carbon_density': 80,
                'biomass_density': 160,
                'description': 'Seasonal dry forest, loses leaves in dry season'
            },
            'mangrove': {
                'rgb_ranges': [
                    {'lower': np.array([0, 20, 0]), 'upper': np.array([80, 120, 80])},    # Very dark green
                    {'lower': np.array([10, 30, 10]), 'upper': np.array([90, 130, 90])},  # Dark green-blue
                    {'lower': np.array([5, 25, 5]), 'upper': np.array([85, 125, 85])},    # Near-black green
                    {'lower': np.array([0, 40, 20]), 'upper': np.array([70, 140, 100])}   # Blue-green tint
                ],
                'ndvi_threshold': 0.4,  # High for healthy mangroves
                'texture_features': {'homogeneity': 0.8, 'contrast': 0.2},
                'carbon_density': 150,  # High carbon storage
                'biomass_density': 300,
                'description': 'Coastal wetland forest with exceptional carbon storage'
            },
            'bamboo_forest': {
                'rgb_ranges': [
                    {'lower': np.array([30, 60, 20]), 'upper': np.array([140, 200, 140])},  # Bright green
                    {'lower': np.array([40, 70, 30]), 'upper': np.array([150, 210, 150])},
                    {'lower': np.array([50, 80, 40]), 'upper': np.array([160, 220, 160])}
                ],
                'ndvi_threshold': 0.35,
                'texture_features': {'homogeneity': 0.5, 'contrast': 0.5},
                'carbon_density': 60,
                'biomass_density': 120,
                'description': 'Fast-growing bamboo stands'
            },
            'melaleuca': {
                'rgb_ranges': [
                    {'lower': np.array([10, 40, 10]), 'upper': np.array([100, 150, 100])},
                    {'lower': np.array([20, 50, 20]), 'upper': np.array([110, 160, 110])},
                    {'lower': np.array([15, 45, 15]), 'upper': np.array([105, 155, 105])}
                ],
                'ndvi_threshold': 0.35,
                'texture_features': {'homogeneity': 0.7, 'contrast': 0.3},
                'carbon_density': 100,
                'biomass_density': 200,
                'description': 'Wetland forest dominated by Melaleuca (paper bark) trees'
            },
            'planted_acacia': {
                'rgb_ranges': [
                    {'lower': np.array([20, 50, 10]), 'upper': np.array([120, 170, 110])},
                    {'lower': np.array([30, 60, 20]), 'upper': np.array([130, 180, 120])},
                    {'lower': np.array([25, 55, 15]), 'upper': np.array([125, 175, 115])}
                ],
                'ndvi_threshold': 0.3,
                'texture_features': {'homogeneity': 0.6, 'contrast': 0.4},
                'carbon_density': 70,
                'biomass_density': 140,
                'description': 'Commercial timber plantation, typically Acacia mangium'
            }
        }
        
        # General forest types (legacy support)
        self.forest_types = {
            'dense_tropical': {
                'rgb_lower': np.array([20, 40, 20]),    # Dark green
                'rgb_upper': np.array([80, 120, 80]),
                'carbon_density': 150.0,  # tC/ha (typical for dense tropical)
                'biomass_density': 300.0,  # t/ha
                'description': 'Dense tropical forest with high carbon content'
            },
            'medium_tropical': {
                'rgb_lower': np.array([40, 60, 30]),    # Medium green
                'rgb_upper': np.array([100, 140, 90]),
                'carbon_density': 100.0,  # tC/ha
                'biomass_density': 200.0,  # t/ha
                'description': 'Medium density tropical forest'
            },
            'light_forest': {
                'rgb_lower': np.array([60, 80, 40]),    # Light green
                'rgb_upper': np.array([120, 160, 110]),
                'carbon_density': 60.0,   # tC/ha
                'biomass_density': 120.0,  # t/ha
                'description': 'Light forest or woodland'
            },
            'young_plantation': {
                'rgb_lower': np.array([80, 100, 60]),   # Very light green
                'rgb_upper': np.array([140, 180, 130]),
                'carbon_density': 30.0,   # tC/ha
                'biomass_density': 60.0,   # t/ha
                'description': 'Young plantation or regenerating forest'
            },
            'mangrove': {
                'rgb_lower': np.array([30, 50, 40]),    # Dark green-blue
                'rgb_upper': np.array([90, 110, 100]),
                'carbon_density': 200.0,  # tC/ha (mangroves are carbon-rich)
                'biomass_density': 400.0,  # t/ha
                'description': 'Mangrove forest (high carbon density)'
            }
        }
        
        # Minimum area threshold for forest detection (in pixels)
        self.min_forest_area_pixels = 100
        
        # Confidence thresholds
        self.min_confidence_threshold = 0.6

    def detect_area(self, image_path: str, ecosystem: Ecosystem, scale_factor: float = 1.0, forest_type: str = None) -> Dict[str, Any]:
        """
        Forest area detection using RGB analysis and vegetation indices.
        
        This method detects total forest area without individual bounding boxes.
        
        :param image_path: Path to the image file
        :param ecosystem: Ecosystem object (for compatibility)
        :param scale_factor: Meters per pixel conversion factor
        :param forest_type: Specific forest type selected by user (e.g., 'mangrove', 'evergreen_broadleaf')
        :return: Forest analysis results with total area calculation
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise FileNotFoundError(f"Could not load image at: {image_path}")
            
            logging.info(f"Processing image: {image_path} for forest type: {forest_type or 'automatic'}")
            
            # Step 1: Automatic color spectrum analysis
            spectrum_analysis = self._analyze_color_spectrum(img)
            
            # Step 2: Preprocess image based on detected spectrum
            preprocessed_img = self._preprocess_for_spectrum(img, spectrum_analysis.imagery_type)
            
            # Step 3: Calculate total forest area based on selected forest type
            if forest_type and forest_type in self.vietnamese_forest_signatures:
                # Use specific forest type parameters
                forest_params = self.vietnamese_forest_signatures[forest_type]
                total_area_result = self._calculate_forest_area_by_type(preprocessed_img, forest_type, forest_params, scale_factor)
            else:
                # Detect all forest types and sum the areas
                total_area_result = self._calculate_total_forest_area(preprocessed_img, scale_factor)
            
            # Step 4: Create simple visualization without bounding boxes
            visualization_data = self._create_simple_visualization(img, total_area_result)
            
            # Step 5: Calculate vegetation indices
            vegetation_indices = self._calculate_vegetation_indices(preprocessed_img)
            
            # Step 6: Calculate texture features
            texture_features = self._calculate_texture_features(preprocessed_img)
            
            # Step 7: Calculate confidence metrics
            confidence_metrics = {
                'overall_confidence': total_area_result.get('confidence', 0.8),
                'vegetation_confidence': min(1.0, max(0.0, (vegetation_indices.get('vegetation_strength', 0.0) + 1) / 2)),
                'classification_confidence': total_area_result.get('confidence', 0.8)
            }
            
            # Step 8: VCS-compliant uncertainty assessment
            uncertainty_assessment = self._assess_uncertainty(confidence_metrics, total_area_result['area_ha'])
            
            results = {
                # Basic metrics - Updated field names to match frontend
                'total_forest_area_ha': float(total_area_result['area_ha']),
                'total_area_ha': float(total_area_result['area_ha']),  # Keep for backward compatibility
                'total_area_m2': float(total_area_result['area_ha'] * 10000),
                'forest_coverage_percent': float(total_area_result['coverage_percent']),
                'forest_percentage': float(total_area_result['coverage_percent']),  # Keep for backward compatibility
                'forest_type_selected': forest_type or 'mixed',
                'number_of_forest_regions': 1,  # Since we're not using bounding boxes
                
                # Color spectrum analysis
                'color_spectrum_analysis': {
                    'detected_imagery_type': spectrum_analysis.imagery_type.value,
                    'dominant_colors': spectrum_analysis.dominant_colors,
                    'vegetation_indices': spectrum_analysis.vegetation_indices,
                    'spectral_characteristics': spectrum_analysis.spectral_characteristics,
                    'recommended_analysis_method': spectrum_analysis.recommended_analysis_method
                },
                
                # Forest type information
                'forest_type_info': {
                    'selected_type': forest_type or 'mixed',
                    'description': total_area_result.get('description', ''),
                    'carbon_density_tC_ha': float(total_area_result.get('carbon_density', 100)),
                    'biomass_density_t_ha': float(total_area_result.get('biomass_density', 200))
                },
                
                # Carbon and biomass estimates - Updated to match frontend
                'carbon_metrics': {
                    'weighted_carbon_density_tC_ha': float(total_area_result.get('carbon_density', 100)),
                    'weighted_biomass_density_t_ha': float(total_area_result.get('biomass_density', 200)),
                    'total_carbon_stock_tC': float(total_area_result['area_ha'] * total_area_result.get('carbon_density', 100)),
                    'total_biomass_stock_t': float(total_area_result['area_ha'] * total_area_result.get('biomass_density', 200))
                },
                
                # Legacy fields for compatibility
                'weighted_carbon_density_tC_ha': float(total_area_result.get('carbon_density', 100)),
                'weighted_biomass_density_t_ha': float(total_area_result.get('biomass_density', 200)),
                'total_carbon_stock_tC': float(total_area_result['area_ha'] * total_area_result.get('carbon_density', 100)),
                'total_biomass_stock_t': float(total_area_result['area_ha'] * total_area_result.get('biomass_density', 200)),
                
                # Empty forest regions array (no bounding boxes)
                'forest_regions': [],
                
                # Vegetation indices
                'vegetation_indices': vegetation_indices,
                
                # Quality metrics
                'confidence_metrics': confidence_metrics,
                'uncertainty_assessment': uncertainty_assessment,
                'texture_features': texture_features,
                
                # Technical metadata
                'validation_data': {
                    'input_resolution': (img.shape[1], img.shape[0]),
                    'pixel_scale_factor': scale_factor,
                    'processing_method': 'Total_Area_Detection',
                    'visualization_available': True,
                    'vcs_compliant': True,
                    'forest_type_based': forest_type is not None
                },
                
                # Visualization
                'visualization': visualization_data
            }
            
            logging.info(f"Detected {total_area_result['area_ha']:.2f} ha of forest")
            logging.info(f"Carbon density: {total_area_result.get('carbon_density', 100):.1f} tC/ha")
            
            return results
            
        except FileNotFoundError as e:
            logging.error(f"Image processing failed: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during forest detection: {e}")
            raise

    def _analyze_color_spectrum(self, img: np.ndarray) -> ColorSpectrumAnalysis:
        """Automatically detect the type of imagery based on color spectrum analysis"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        
        # Calculate color statistics
        mean_bgr = np.mean(img, axis=(0, 1))
        std_bgr = np.std(img, axis=(0, 1))
        
        # Calculate dominant colors using k-means
        pixels = img.reshape(-1, 3)
        # Downsample for speed
        sample_size = min(10000, pixels.shape[0])
        sample_indices = np.random.choice(pixels.shape[0], sample_size, replace=False)
        pixel_sample = pixels[sample_indices]
        
        # K-means clustering
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(pixel_sample)
        dominant_colors = [tuple(map(int, color)) for color in kmeans.cluster_centers_]
        
        # Calculate vegetation indices
        b, g, r = cv2.split(img.astype(np.float32) / 255.0)
        
        # Excess Green Index
        exg = 2 * g - r - b
        exg_mean = np.mean(exg)
        
        # Visible Atmospherically Resistant Index
        vari_denom = g + r - b
        vari = np.where(vari_denom != 0, (g - r) / vari_denom, 0)
        vari_mean = np.mean(vari)
        
        # Green Leaf Index
        gli_denom = 2 * g + r + b
        gli = np.where(gli_denom != 0, (2 * g - r - b) / gli_denom, 0)
        gli_mean = np.mean(gli)
        
        # Determine imagery type based on spectral characteristics
        imagery_type = self._classify_imagery_type(mean_bgr, std_bgr, exg_mean, vari_mean)
        
        # Determine recommended analysis method
        if imagery_type == ImageryType.RGB_NATURAL:
            recommended_method = "rgb_vegetation_index_analysis"
        elif imagery_type == ImageryType.FALSE_COLOR:
            recommended_method = "false_color_ndvi_analysis"
        elif imagery_type == ImageryType.MULTISPECTRAL:
            recommended_method = "multispectral_band_analysis"
        else:
            recommended_method = "standard_rgb_analysis"
        
        return ColorSpectrumAnalysis(
            imagery_type=imagery_type,
            dominant_colors=dominant_colors,
            vegetation_indices={
                'excess_green_index': float(exg_mean),
                'vari': float(vari_mean),
                'green_leaf_index': float(gli_mean)
            },
            spectral_characteristics={
                'mean_bgr': mean_bgr.tolist(),
                'std_bgr': std_bgr.tolist(),
                'color_variance': float(np.mean(std_bgr)),
                'brightness': float(np.mean(mean_bgr))
            },
            recommended_analysis_method=recommended_method
        )

    def _classify_imagery_type(self, mean_bgr: np.ndarray, std_bgr: np.ndarray, 
                               exg: float, vari: float) -> ImageryType:
        """Classify the type of imagery based on spectral characteristics"""
        b_mean, g_mean, r_mean = mean_bgr
        
        # Check for false color (NIR in red channel)
        if r_mean > g_mean > b_mean and r_mean / g_mean > 1.3:
            return ImageryType.FALSE_COLOR
        
        # Check for natural RGB
        if abs(exg) < 0.3 and abs(vari) < 0.2:
            return ImageryType.RGB_NATURAL
        
        # Check for processed vegetation index
        if abs(exg) > 0.5 or abs(vari) > 0.4:
            return ImageryType.NDVI
        
        # Default to natural RGB
        return ImageryType.RGB_NATURAL

    def _preprocess_for_spectrum(self, img: np.ndarray, imagery_type: ImageryType) -> np.ndarray:
        """Preprocess image based on detected spectrum type"""
        if imagery_type == ImageryType.FALSE_COLOR:
            # For false color, enhance the NIR channel (usually in red)
            enhanced = img.copy()
            enhanced[:, :, 2] = cv2.equalizeHist(enhanced[:, :, 2])  # Enhance red (NIR)
            return enhanced
        elif imagery_type == ImageryType.NDVI:
            # For NDVI, apply specific preprocessing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.applyColorMap(gray, cv2.COLORMAP_SPRING)
            return enhanced
        else:
            # Standard preprocessing for natural RGB
            return self._preprocess_image(img)
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Advanced image preprocessing for forest analysis."""
        # Noise reduction with bilateral filter (preserves edges)
        denoised = cv2.bilateralFilter(img, 9, 75, 75)
        
        # Enhance contrast using CLAHE on LAB color space
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Gamma correction for better vegetation visibility
        gamma = 1.2
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        gamma_corrected = cv2.LUT(enhanced_img, table)
        
        return gamma_corrected

    def _detect_forest_regions(self, img: np.ndarray, scale_factor: float) -> List[ForestRegion]:
        """Detect individual forest regions and create bounding boxes"""
        forest_regions = []
        height, width = img.shape[:2]
        
        # Create a combined mask for all forest types
        combined_mask = np.zeros((height, width), dtype=np.uint8)
        forest_type_masks = {}
        
        # Detect each Vietnamese forest type
        for forest_type, params in self.vietnamese_forest_signatures.items():
            type_mask = np.zeros((height, width), dtype=np.uint8)
            
            # Apply all RGB ranges for this forest type
            for rgb_range in params['rgb_ranges']:
                mask = cv2.inRange(img, rgb_range['lower'], rgb_range['upper'])
                type_mask = cv2.bitwise_or(type_mask, mask)
            
            # Morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            type_mask = cv2.morphologyEx(type_mask, cv2.MORPH_OPEN, kernel, iterations=2)
            type_mask = cv2.morphologyEx(type_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            forest_type_masks[forest_type] = type_mask
            combined_mask = cv2.bitwise_or(combined_mask, type_mask)
        
        # Find contours in the combined mask
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for contour in contours:
            area_pixels = cv2.contourArea(contour)
            
            # Skip small regions
            if area_pixels < self.min_forest_area_pixels:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate area in hectares
            pixel_area_m2 = scale_factor ** 2
            area_m2 = area_pixels * pixel_area_m2
            area_hectares = area_m2 / 10000
            
            # Determine forest type for this region
            region_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.drawContours(region_mask, [contour], -1, 255, -1)
            
            best_forest_type = None
            best_overlap = 0
            
            for forest_type, type_mask in forest_type_masks.items():
                overlap = cv2.bitwise_and(region_mask, type_mask)
                overlap_area = cv2.countNonZero(overlap)
                
                if overlap_area > best_overlap:
                    best_overlap = overlap_area
                    best_forest_type = forest_type
            
            if best_forest_type is None:
                continue
            
            # Extract region for detailed analysis
            region_img = img[y:y+h, x:x+w]
            
            # Analyze forest density and health
            density = self._analyze_forest_density(region_img)
            health_status = self._analyze_forest_health(region_img)
            
            # Calculate confidence based on various factors
            confidence = self._calculate_region_confidence(
                region_img, area_pixels, best_overlap / area_pixels
            )
            
            if confidence < self.min_confidence_threshold:
                continue
            
            # Get carbon and biomass estimates
            forest_params = self.vietnamese_forest_signatures[best_forest_type]
            
            # Adjust carbon density based on forest density and health
            base_carbon = forest_params['carbon_density']
            density_factor = {'dense': 1.2, 'medium': 1.0, 'sparse': 0.7}[density]
            health_factor = {'healthy': 1.0, 'stressed': 0.8, 'degraded': 0.6}[health_status]
            
            adjusted_carbon = base_carbon * density_factor * health_factor
            adjusted_biomass = forest_params['biomass_density'] * density_factor * health_factor
            
            forest_regions.append(ForestRegion(
                bbox=(x, y, w, h),
                area_pixels=int(area_pixels),
                area_hectares=area_hectares,
                confidence=confidence,
                forest_type=best_forest_type,
                density=density,
                health_status=health_status,
                carbon_density_estimate=adjusted_carbon,
                biomass_density_estimate=adjusted_biomass
            ))
        
        # Sort regions by area (largest first)
        forest_regions.sort(key=lambda r: r.area_hectares, reverse=True)
        
        return forest_regions

    def _analyze_forest_density(self, region_img: np.ndarray) -> str:
        """Analyze forest density based on color and texture"""
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture variance
        texture_var = np.var(gray)
        
        # Calculate green channel intensity
        green_mean = np.mean(region_img[:, :, 1])
        
        # Classify density
        if texture_var > 1500 and green_mean < 80:
            return 'dense'
        elif texture_var > 800 and green_mean < 120:
            return 'medium'
        else:
            return 'sparse'

    def _analyze_forest_health(self, region_img: np.ndarray) -> str:
        """Analyze forest health based on color patterns"""
        # Calculate color statistics
        b, g, r = cv2.split(region_img)
        
        # Green ratio (healthy forests have higher green)
        green_ratio = np.mean(g) / (np.mean(r) + np.mean(b) + 1e-6)
        
        # Brown/yellow detection (unhealthy indicator)
        brown_mask = cv2.inRange(region_img, 
                                np.array([20, 30, 40]), 
                                np.array([80, 90, 120]))
        brown_ratio = cv2.countNonZero(brown_mask) / (region_img.shape[0] * region_img.shape[1])
        
        # Classify health
        if green_ratio > 0.6 and brown_ratio < 0.1:
            return 'healthy'
        elif green_ratio > 0.4 and brown_ratio < 0.3:
            return 'stressed'
        else:
            return 'degraded'

    def _calculate_region_confidence(self, region_img: np.ndarray, area_pixels: float, 
                                   type_match_ratio: float) -> float:
        """Calculate confidence score for a detected forest region"""
        # Factor 1: Size (larger regions are more reliable)
        size_score = min(1.0, area_pixels / 10000)  # Normalize to max at 10000 pixels
        
        # Factor 2: Type match ratio
        type_score = type_match_ratio
        
        # Factor 3: Color consistency
        color_std = np.std(region_img, axis=(0, 1))
        color_consistency = 1.0 / (1.0 + np.mean(color_std) / 50.0)
        
        # Factor 4: Edge density (forests have moderate edge density)
        gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = cv2.countNonZero(edges) / (gray.shape[0] * gray.shape[1])
        edge_score = 1.0 - abs(edge_density - 0.15) / 0.15  # Optimal around 15%
        
        # Combine scores
        confidence = (size_score * 0.2 + type_score * 0.4 + 
                     color_consistency * 0.2 + edge_score * 0.2)
        
        return min(1.0, max(0.0, confidence))

    def _calculate_vegetation_indices(self, img: np.ndarray) -> Dict[str, float]:
        """Calculate vegetation indices from RGB image."""
        # Convert to float for calculations
        img_float = img.astype(np.float32) / 255.0
        b, g, r = cv2.split(img_float)
        
        # Visible Atmospherically Resistant Index (VARI)
        # VARI = (Green - Red) / (Green + Red - Blue)
        denominator = g + r - b
        vari = np.where(denominator != 0, (g - r) / denominator, 0)
        vari_mean = np.mean(vari)
        
        # Excess Green Index (ExG)
        # ExG = 2*Green - Red - Blue
        exg = 2 * g - r - b
        exg_mean = np.mean(exg)
        
        # Green Leaf Index (GLI)
        # GLI = (2*Green - Red - Blue) / (2*Green + Red + Blue)
        denominator_gli = 2 * g + r + b
        gli = np.where(denominator_gli != 0, (2 * g - r - b) / denominator_gli, 0)
        gli_mean = np.mean(gli)
        
        # RGB-based NDVI approximation
        # Approximation: (Green - Red) / (Green + Red)
        denominator_ndvi = g + r
        ndvi_approx = np.where(denominator_ndvi != 0, (g - r) / denominator_ndvi, 0)
        ndvi_approx_mean = np.mean(ndvi_approx)
        
        return {
            'vari': float(vari_mean),
            'exg': float(exg_mean),
            'gli': float(gli_mean),
            'ndvi_approximation': float(ndvi_approx_mean),
            'vegetation_strength': float((vari_mean + exg_mean + gli_mean) / 3)
        }

    def _classify_forest_types(self, img: np.ndarray, scale_factor: float) -> List[ForestClassification]:
        """Classify different forest types using RGB analysis."""
        classifications = []
        total_pixels = img.shape[0] * img.shape[1]
        pixel_area_m2 = scale_factor ** 2
        
        for forest_type, params in self.forest_types.items():
            # Create mask for this forest type
            mask = cv2.inRange(img, params['rgb_lower'], params['rgb_upper'])
            
            # Clean up the mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Calculate area
            forest_pixels = cv2.countNonZero(mask)
            if forest_pixels > 0:
                area_m2 = forest_pixels * pixel_area_m2
                area_ha = area_m2 / 10000
                
                # Calculate confidence based on color consistency and spatial coherence
                confidence = self._calculate_forest_type_confidence(img, mask, params)
                
                # Only include if confidence is above threshold and area is significant
                if confidence > 0.3 and area_ha > 0.01:  # Minimum 0.01 ha (100 m²)
                    classifications.append(ForestClassification(
                        forest_type=forest_type,
                        confidence=confidence,
                        carbon_density=params['carbon_density'],
                        biomass_density=params['biomass_density'],
                        area_ha=area_ha
                    ))
        
        return classifications

    def _calculate_forest_type_confidence(self, img: np.ndarray, mask: np.ndarray, params: Dict) -> float:
        """Calculate confidence score for forest type classification."""
        if cv2.countNonZero(mask) == 0:
            return 0.0
        
        # Extract pixels within the mask
        masked_pixels = img[mask > 0]
        
        # Calculate color consistency
        color_std = np.std(masked_pixels, axis=0)
        color_consistency = 1.0 / (1.0 + np.mean(color_std) / 50.0)  # Normalize by expected variation
        
        # Calculate spatial coherence (how clustered the forest areas are)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            # Prefer fewer, larger contours over many small scattered ones
            total_area = cv2.countNonZero(mask)
            largest_contour_area = max(cv2.contourArea(c) for c in contours)
            spatial_coherence = largest_contour_area / total_area
        else:
            spatial_coherence = 0.0
        
        # Calculate color range fit
        lower_bound = params['rgb_lower']
        upper_bound = params['rgb_upper']
        range_center = (lower_bound + upper_bound) / 2
        mean_color = np.mean(masked_pixels, axis=0)
        color_distance = np.linalg.norm(mean_color - range_center)
        max_distance = np.linalg.norm(upper_bound - lower_bound) / 2
        color_fit = max(0, 1.0 - color_distance / max_distance)
        
        # Combine metrics
        confidence = (color_consistency * 0.4 + spatial_coherence * 0.3 + color_fit * 0.3)
        return min(1.0, max(0.0, confidence))

    def _calculate_texture_features(self, img: np.ndarray) -> Dict[str, float]:
        """Calculate texture features for forest health assessment."""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture using Local Binary Pattern approximation
        # Simplified version using gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Texture metrics
        texture_variance = np.var(gradient_magnitude)
        texture_mean = np.mean(gradient_magnitude)
        
        # Edge density (indicator of forest structure complexity)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
        
        return {
            'texture_variance': float(texture_variance),
            'texture_mean': float(texture_mean),
            'edge_density': float(edge_density),
            'structural_complexity': float((texture_variance / 1000 + edge_density) / 2)
        }

    def _calculate_weighted_carbon_density(self, classifications: List[ForestClassification]) -> float:
        """Calculate area-weighted carbon density."""
        if not classifications:
            return 0.0
        
        total_area = sum(fc.area_ha for fc in classifications)
        if total_area == 0:
            return 0.0
        
        weighted_sum = sum(fc.carbon_density * fc.area_ha for fc in classifications)
        return weighted_sum / total_area

    def _calculate_weighted_biomass_density(self, classifications: List[ForestClassification]) -> float:
        """Calculate area-weighted biomass density."""
        if not classifications:
            return 0.0
        
        total_area = sum(fc.area_ha for fc in classifications)
        if total_area == 0:
            return 0.0
        
        weighted_sum = sum(fc.biomass_density * fc.area_ha for fc in classifications)
        return weighted_sum / total_area

    def _calculate_confidence_metrics(self, img: np.ndarray, forest_regions: List[ForestRegion], 
                                    vegetation_indices: Dict[str, float], texture_features: Dict[str, float]) -> Dict[str, float]:
        """Calculate comprehensive confidence metrics."""
        if not forest_regions:
            return {'overall_confidence': 0.0, 'classification_confidence': 0.0, 'vegetation_confidence': 0.0}
        
        # Classification confidence (weighted by area)
        total_area = sum(r.area_hectares for r in forest_regions)
        classification_confidence = sum(r.confidence * r.area_hectares for r in forest_regions) / total_area if total_area > 0 else 0.0
        
        # Vegetation index confidence
        vegetation_strength = vegetation_indices.get('vegetation_strength', 0.0)
        vegetation_confidence = min(1.0, max(0.0, (vegetation_strength + 1) / 2))  # Normalize to 0-1
        
        # Texture confidence (higher structural complexity suggests healthier forest)
        structural_complexity = texture_features.get('structural_complexity', 0.0)
        texture_confidence = min(1.0, max(0.0, structural_complexity))
        
        # Overall confidence
        overall_confidence = (classification_confidence * 0.5 + vegetation_confidence * 0.3 + texture_confidence * 0.2)
        
        return {
            'overall_confidence': float(overall_confidence),
            'classification_confidence': float(classification_confidence),
            'vegetation_confidence': float(vegetation_confidence),
            'texture_confidence': float(texture_confidence)
        }

    def _assess_uncertainty(self, confidence_metrics: Dict[str, float], total_area: float) -> Dict[str, Any]:
        """VCS-compliant uncertainty assessment."""
        overall_confidence = confidence_metrics.get('overall_confidence', 0.0)
        
        # VCS uncertainty categories
        if overall_confidence >= 0.8:
            uncertainty_level = 'low'
            uncertainty_percentage = 10.0
        elif overall_confidence >= 0.6:
            uncertainty_level = 'medium'
            uncertainty_percentage = 20.0
        else:
            uncertainty_level = 'high'
            uncertainty_percentage = 35.0
        
        # Area-based uncertainty adjustment
        if total_area < 1.0:  # Less than 1 hectare
            uncertainty_percentage += 10.0
            uncertainty_level = 'high'
        
        return {
            'uncertainty_level': uncertainty_level,
            'uncertainty_percentage': float(uncertainty_percentage),
            'confidence_score': float(overall_confidence),
            'vcs_compliant': True,
            'recommended_buffer': float(uncertainty_percentage * 1.5)  # Conservative buffer
        }

    def _create_forest_visualization(self, img: np.ndarray, classifications: List[ForestClassification]) -> Dict[str, Any]:
        """Create visualization data for forest classification results."""
        # Create a color-coded visualization
        visualization = img.copy()
        
        # Color map for different forest types
        colors = {
            'dense_tropical': (0, 100, 0),      # Dark green
            'medium_tropical': (0, 150, 0),     # Medium green
            'light_forest': (0, 200, 0),        # Light green
            'young_plantation': (0, 255, 100),  # Very light green
            'mangrove': (100, 150, 0)           # Blue-green
        }
        
        overlay = np.zeros_like(img)
        
        for fc in classifications:
            if fc.forest_type in self.forest_types:
                params = self.forest_types[fc.forest_type]
                mask = cv2.inRange(img, params['rgb_lower'], params['rgb_upper'])
                
                # Clean up mask
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
                
                # Apply color overlay
                color = colors.get(fc.forest_type, (0, 255, 0))
                overlay[mask > 0] = color
        
        # Blend with original image
        alpha = 0.4
        visualization = cv2.addWeighted(img, 1-alpha, overlay, alpha, 0)
        
        return {
            'has_visualization': True,
            'overlay_alpha': alpha,
            'forest_type_colors': colors,
            'description': 'Color-coded forest type classification overlay'
        }

    def _create_visualization(self, original_img: np.ndarray, forest_regions: List[ForestRegion]) -> Dict[str, Any]:
        """Create visualization with bounding boxes and transformation display"""
        # Create output image with bounding boxes
        output_img = original_img.copy()
        
        # Define colors for different forest types
        forest_colors = {
            'evergreen_broadleaf': (0, 100, 0),      # Dark green
            'deciduous_dipterocarp': (0, 150, 0),   # Medium green
            'mangrove': (100, 150, 0),              # Blue-green
            'bamboo_forest': (0, 200, 100),         # Light green
            'melaleuca': (50, 150, 50),             # Mixed green
            'planted_acacia': (0, 255, 0)           # Bright green
        }
        
        # Draw bounding boxes and labels
        for i, region in enumerate(forest_regions):
            x, y, w, h = region.bbox
            color = forest_colors.get(region.forest_type, (0, 255, 0))
            
            # Draw bounding box
            cv2.rectangle(output_img, (x, y), (x + w, y + h), color, 2)
            
            # Prepare label
            label = f"{region.forest_type.replace('_', ' ').title()}"
            label2 = f"{region.area_hectares:.1f} ha | {region.density}"
            label3 = f"Carbon: {region.carbon_density_estimate:.0f} tC/ha"
            
            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label2_size, _ = cv2.getTextSize(label2, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            label3_size, _ = cv2.getTextSize(label3, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            
            max_width = max(label_size[0], label2_size[0], label3_size[0])
            
            cv2.rectangle(output_img, (x, y - 50), (x + max_width + 10, y), (255, 255, 255), -1)
            cv2.rectangle(output_img, (x, y - 50), (x + max_width + 10, y), color, 2)
            
            # Draw text
            cv2.putText(output_img, label, (x + 5, y - 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(output_img, label2, (x + 5, y - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            cv2.putText(output_img, label3, (x + 5, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Convert images to base64 for web display
        _, original_buffer = cv2.imencode('.jpg', original_img)
        original_base64 = base64.b64encode(original_buffer).decode('utf-8')
        
        _, output_buffer = cv2.imencode('.jpg', output_img)
        output_base64 = base64.b64encode(output_buffer).decode('utf-8')
        
        # Create heatmap overlay
        heatmap = np.zeros((original_img.shape[0], original_img.shape[1]), dtype=np.float32)
        
        for region in forest_regions:
            x, y, w, h = region.bbox
            # Create gradient based on carbon density
            intensity = region.carbon_density_estimate / 250.0  # Normalize to 0-1
            heatmap[y:y+h, x:x+w] = intensity
        
        # Apply Gaussian blur for smooth heatmap
        heatmap = cv2.GaussianBlur(heatmap, (21, 21), 0)
        
        # Convert heatmap to color
        heatmap_normalized = (heatmap * 255).astype(np.uint8)
        heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)
        
        # Blend with original
        heatmap_overlay = cv2.addWeighted(original_img, 0.7, heatmap_colored, 0.3, 0)
        
        _, heatmap_buffer = cv2.imencode('.jpg', heatmap_overlay)
        heatmap_base64 = base64.b64encode(heatmap_buffer).decode('utf-8')
        
        return {
            'has_visualization': True,
            'original_image_base64': original_base64,
            'annotated_image_base64': output_base64,
            'heatmap_overlay_base64': heatmap_base64,
            'visualization_type': 'before_after_transformation',
            'bounding_boxes_count': len(forest_regions),
            'forest_types_detected': list(set(r.forest_type for r in forest_regions)),
            'description': 'Automatic forest detection with bounding boxes and carbon density heatmap'
        }

    def _calculate_forest_area_by_type(self, img: np.ndarray, forest_type: str, forest_params: Dict, scale_factor: float) -> Dict[str, Any]:
        """Calculate forest area for a specific forest type with improved detection"""
        height, width = img.shape[:2]
        total_pixels = height * width
        
        # First use simple detection to get general forest areas
        simple_result = self._simple_forest_detection(img, scale_factor)
        general_forest_mask = simple_result['mask']
        
        # If simple detection found very little, relax the constraints
        if simple_result['coverage_percent'] < 1.0:
            logging.warning(f"Simple detection found only {simple_result['coverage_percent']:.2f}% forest, using relaxed detection")
            # Try with more relaxed parameters
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # Even broader HSV range
            lower_green_hsv = np.array([20, 15, 15])
            upper_green_hsv = np.array([100, 255, 255])
            general_forest_mask = cv2.inRange(hsv, lower_green_hsv, upper_green_hsv)
            
            # Clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            general_forest_mask = cv2.morphologyEx(general_forest_mask, cv2.MORPH_CLOSE, kernel)
        
        # Now look for specific forest type within general forest areas
        type_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Apply RGB ranges for the specific forest type
        for rgb_range in forest_params['rgb_ranges']:
            mask = cv2.inRange(img, rgb_range['lower'], rgb_range['upper'])
            type_mask = cv2.bitwise_or(type_mask, mask)
        
        # Combine with general forest mask (if we have one)
        if cv2.countNonZero(general_forest_mask) > 100:
            type_mask = cv2.bitwise_and(type_mask, general_forest_mask)
        
        # If still too little detected, use the general forest mask
        if cv2.countNonZero(type_mask) < total_pixels * 0.001:  # Less than 0.1%
            logging.info(f"Specific forest type detection too low, using general forest mask")
            type_mask = general_forest_mask
        
        # Calculate area
        forest_pixels = cv2.countNonZero(type_mask)
        pixel_area_m2 = scale_factor ** 2
        area_m2 = forest_pixels * pixel_area_m2
        area_ha = area_m2 / 10000
        
        # Calculate coverage percentage
        coverage_percent = (forest_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        # Health and carbon analysis
        if forest_pixels > 0:
            # Extract forest pixels for analysis
            forest_pixel_values = img[type_mask > 0]
            
            if len(forest_pixel_values) > 0:
                b_mean = np.mean(forest_pixel_values[:, 0])
                g_mean = np.mean(forest_pixel_values[:, 1])
                r_mean = np.mean(forest_pixel_values[:, 2])
                
                # Health based on greenness relative to other channels
                greenness = g_mean / (r_mean + b_mean + g_mean + 1e-6)
                health_factor = min(1.0, max(0.5, greenness * 3))  # Scale to 0.5-1.0
            else:
                health_factor = 0.7
            
            # Adjust carbon density based on health
            base_carbon = forest_params['carbon_density']
            adjusted_carbon = base_carbon * (0.7 + 0.3 * health_factor)
            
            confidence = min(0.9, forest_pixels / (total_pixels * 0.01))  # 1% coverage = 90% confidence
        else:
            adjusted_carbon = forest_params['carbon_density']
            confidence = 0.0
            health_factor = 0.0
        
        logging.info(f"Forest type {forest_type}: {forest_pixels} pixels detected, {area_ha:.2f} ha, {coverage_percent:.1f}%")
        
        return {
            'area_ha': area_ha,
            'coverage_percent': coverage_percent,
            'carbon_density': adjusted_carbon,
            'biomass_density': forest_params['biomass_density'],
            'confidence': confidence,
            'description': forest_params['description'],
            'mask': type_mask,
            'health_factor': health_factor
        }
    
    def _calculate_total_forest_area(self, img: np.ndarray, scale_factor: float) -> Dict[str, Any]:
        """Calculate total forest area across all forest types with improved detection"""
        height, width = img.shape[:2]
        total_pixels = height * width
        
        # First use simple detection
        simple_result = self._simple_forest_detection(img, scale_factor)
        
        # If simple detection found reasonable forest coverage, try to classify types
        if simple_result['coverage_percent'] > 0.5:
            # Try to detect specific forest types
            combined_mask = np.zeros((height, width), dtype=np.uint8)
            total_weighted_carbon = 0
            total_weighted_biomass = 0
            detected_types = []
            
            for forest_type, params in self.vietnamese_forest_signatures.items():
                type_mask = np.zeros((height, width), dtype=np.uint8)
                
                # Apply RGB ranges for this forest type
                for rgb_range in params['rgb_ranges']:
                    mask = cv2.inRange(img, rgb_range['lower'], rgb_range['upper'])
                    type_mask = cv2.bitwise_or(type_mask, mask)
                
                # Combine with simple forest mask
                type_mask = cv2.bitwise_and(type_mask, simple_result['mask'])
                
                # Calculate area for this type
                type_pixels = cv2.countNonZero(type_mask)
                if type_pixels > 100:  # Minimum threshold
                    pixel_area_m2 = scale_factor ** 2
                    type_area_ha = (type_pixels * pixel_area_m2) / 10000
                    total_weighted_carbon += params['carbon_density'] * type_area_ha
                    total_weighted_biomass += params['biomass_density'] * type_area_ha
                    detected_types.append(forest_type)
                    
                    # Add to combined mask
                    combined_mask = cv2.bitwise_or(combined_mask, type_mask)
            
            # If no specific types detected, use the simple detection mask
            if cv2.countNonZero(combined_mask) < 100:
                combined_mask = simple_result['mask']
                detected_types = ['general_vegetation']
        else:
            # If simple detection found very little, use it as is
            combined_mask = simple_result['mask']
            detected_types = ['general_vegetation']
            total_weighted_carbon = simple_result['area_ha'] * 100  # Default carbon density
            total_weighted_biomass = simple_result['area_ha'] * 200  # Default biomass density
        
        # Calculate final metrics
        forest_pixels = cv2.countNonZero(combined_mask)
        pixel_area_m2 = scale_factor ** 2
        area_m2 = forest_pixels * pixel_area_m2
        area_ha = area_m2 / 10000
        coverage_percent = (forest_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        # Calculate average carbon density
        if area_ha > 0 and len(detected_types) > 0 and detected_types[0] != 'general_vegetation':
            avg_carbon_density = total_weighted_carbon / area_ha
            avg_biomass_density = total_weighted_biomass / area_ha
        else:
            # Use general forest average
            avg_carbon_density = 100  # Default tC/ha for mixed forest
            avg_biomass_density = 200  # Default t/ha for mixed forest
        
        confidence = min(0.8, forest_pixels / (total_pixels * 0.01))  # 1% = 80% confidence
        
        logging.info(f"Total forest detection: {forest_pixels} pixels, {area_ha:.2f} ha, {coverage_percent:.1f}%")
        logging.info(f"Detected forest types: {detected_types}")
        
        return {
            'area_ha': area_ha,
            'coverage_percent': coverage_percent,
            'carbon_density': avg_carbon_density,
            'biomass_density': avg_biomass_density,
            'confidence': confidence,
            'description': f'Forest types: {", ".join(detected_types)}',
            'mask': combined_mask,
            'detected_types': detected_types
        }
    
    def _create_simple_visualization(self, original_img: np.ndarray, area_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create simple visualization showing forest areas without bounding boxes"""
        # Create output image with forest overlay
        output_img = original_img.copy()
        
        # Get the forest mask
        mask = area_result.get('mask', np.zeros_like(original_img[:, :, 0]))
        
        # Create green overlay for forest areas
        overlay = np.zeros_like(original_img)
        overlay[mask > 0] = [0, 255, 0]  # Green color for forest
        
        # Blend with original image
        alpha = 0.3
        output_img = cv2.addWeighted(original_img, 1-alpha, overlay, alpha, 0)
        
        # Add text information
        text_info = [
            f"Forest Area: {area_result['area_ha']:.1f} ha",
            f"Coverage: {area_result['coverage_percent']:.1f}%",
            f"Carbon: {area_result['carbon_density']:.0f} tC/ha"
        ]
        
        y_offset = 30
        for text in text_info:
            cv2.putText(output_img, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(output_img, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
            y_offset += 30
        
        # Convert images to base64 for web display
        _, original_buffer = cv2.imencode('.jpg', original_img)
        original_base64 = base64.b64encode(original_buffer).decode('utf-8')
        
        _, output_buffer = cv2.imencode('.jpg', output_img)
        output_base64 = base64.b64encode(output_buffer).decode('utf-8')
        
        # Create heatmap based on carbon density
        heatmap = np.zeros((original_img.shape[0], original_img.shape[1]), dtype=np.float32)
        heatmap[mask > 0] = area_result['carbon_density'] / 250.0  # Normalize to 0-1
        
        # Apply Gaussian blur for smooth heatmap
        heatmap = cv2.GaussianBlur(heatmap, (21, 21), 0)
        
        # Convert heatmap to color
        heatmap_normalized = (heatmap * 255).astype(np.uint8)
        heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)
        
        # Blend with original
        heatmap_overlay = cv2.addWeighted(original_img, 0.7, heatmap_colored, 0.3, 0)
        
        _, heatmap_buffer = cv2.imencode('.jpg', heatmap_overlay)
        heatmap_base64 = base64.b64encode(heatmap_buffer).decode('utf-8')
        
        return {
            'has_visualization': True,
            'original_image_base64': original_base64,
            'annotated_image_base64': output_base64,
            'heatmap_overlay_base64': heatmap_base64,
            'visualization_type': 'simple_forest_overlay',
            'description': 'Forest area detection with overlay visualization'
        }

    def _simple_forest_detection(self, img: np.ndarray, scale_factor: float) -> Dict[str, Any]:
        """Simple but effective forest detection using HSV and multiple methods"""
        height, width = img.shape[:2]
        total_pixels = height * width
        
        # Try AI detection first if available
        if AI_DETECTOR_AVAILABLE:
            try:
                logging.info("Using AI-powered forest detection")
                ai_result = ai_forest_detector.detect_forest_comprehensive(img, scale_factor)
                
                # If AI detection found significant forest, use it
                if ai_result.coverage_percent > 1.0:
                    logging.info(f"AI detection successful: {ai_result.coverage_percent:.1f}% coverage, {ai_result.area_ha:.2f} ha")
                    return {
                        'mask': ai_result.forest_mask,
                        'area_ha': ai_result.area_ha,
                        'coverage_percent': ai_result.coverage_percent,
                        'forest_pixels': ai_result.forest_pixels,
                        'detection_method': ai_result.detection_method,
                        'confidence': ai_result.confidence_score
                    }
                else:
                    logging.info("AI detection found minimal forest, trying traditional methods")
            except Exception as e:
                logging.warning(f"AI detection failed: {e}. Falling back to traditional methods.")
        
        # Traditional detection methods
        logging.info("Using traditional forest detection methods")
        
        # Convert to different color spaces
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        
        # Method 1: HSV-based green detection (very broad range)
        # Hue: 25-95 (yellow-green to blue-green)
        # Saturation: 20-255 (include even desaturated greens)  
        # Value: 20-255 (include dark forests)
        lower_green_hsv = np.array([25, 20, 20])
        upper_green_hsv = np.array([95, 255, 255])
        hsv_mask = cv2.inRange(hsv, lower_green_hsv, upper_green_hsv)
        
        # Method 2: LAB color space (better for vegetation)
        # A channel < 127 indicates green
        l, a, b_channel = cv2.split(lab)
        lab_mask = (a < 127).astype(np.uint8) * 255
        
        # Method 3: Simple RGB ratios
        b, g, r = cv2.split(img)
        # Vegetation has more green than red and blue
        rgb_mask = ((g > r * 0.8) & (g > b * 0.8)).astype(np.uint8) * 255
        
        # Method 4: Excess Green Index
        exg = 2.0 * g.astype(float) - r.astype(float) - b.astype(float)
        exg_mask = (exg > 10).astype(np.uint8) * 255
        
        # Debug: save individual masks
        debug_dir = "/tmp/forest_debug"
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(f"{debug_dir}/hsv_mask.jpg", hsv_mask)
        cv2.imwrite(f"{debug_dir}/lab_mask.jpg", lab_mask)
        cv2.imwrite(f"{debug_dir}/rgb_mask.jpg", rgb_mask)
        cv2.imwrite(f"{debug_dir}/exg_mask.jpg", exg_mask)
        
        # Combine all masks with voting
        combined = hsv_mask.astype(float) + lab_mask.astype(float) + rgb_mask.astype(float) + exg_mask.astype(float)
        # At least 2 methods must agree
        forest_mask = (combined >= 2 * 255).astype(np.uint8) * 255
        
        # Save combined mask before cleanup
        cv2.imwrite(f"{debug_dir}/combined_before_cleanup.jpg", forest_mask)
        
        # Clean up with morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        forest_mask = cv2.morphologyEx(forest_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Remove very small components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(forest_mask, connectivity=8)
        min_size = 50  # Minimum component size
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] < min_size:
                forest_mask[labels == i] = 0
        
        # Save final mask
        cv2.imwrite(f"{debug_dir}/final_forest_mask.jpg", forest_mask)
        
        # Calculate metrics
        forest_pixels = cv2.countNonZero(forest_mask)
        pixel_area_m2 = scale_factor ** 2
        area_m2 = forest_pixels * pixel_area_m2
        area_ha = area_m2 / 10000
        coverage_percent = (forest_pixels / total_pixels) * 100
        
        # Log pixel values for debugging
        logging.info(f"Image shape: {img.shape}")
        logging.info(f"Mean RGB values: R={np.mean(r):.1f}, G={np.mean(g):.1f}, B={np.mean(b):.1f}")
        logging.info(f"HSV mask pixels: {cv2.countNonZero(hsv_mask)}")
        logging.info(f"LAB mask pixels: {cv2.countNonZero(lab_mask)}")
        logging.info(f"RGB mask pixels: {cv2.countNonZero(rgb_mask)}")
        logging.info(f"EXG mask pixels: {cv2.countNonZero(exg_mask)}")
        logging.info(f"Traditional detection: {forest_pixels} pixels ({coverage_percent:.1f}%), {area_ha:.2f} ha")
        
        return {
            'mask': forest_mask,
            'area_ha': area_ha,
            'coverage_percent': coverage_percent,
            'forest_pixels': forest_pixels,
            'detection_method': 'Traditional Multi-Method Detection',
            'confidence': 0.7  # Default confidence for traditional methods
        }

    def detect_area_comprehensive(self, image: np.ndarray, scale_factor: float = 1.0, 
                                 forest_type: Optional[str] = None, use_ai: bool = True) -> Dict[str, Any]:
        """
        Comprehensive forest detection using AI models when available, with fallback to traditional methods.
        
        Args:
            image: Input image as numpy array
            scale_factor: Meters per pixel
            forest_type: Specific forest type to detect
            use_ai: Whether to attempt AI detection first
            
        Returns:
            Dictionary with detection results including AI confidence scores
        """
        # Try AI detection first if requested and available
        ai_result = None
        if use_ai:
            try:
                from app.services.ai_forest_detector import ai_forest_detector
                ai_result = ai_forest_detector.detect_forest_comprehensive(
                    image, scale_factor, forest_type
                )
                
                if ai_result and ai_result.coverage_percent > 0:
                    # Convert AI result to standard format
                    return {
                        'forest_mask': ai_result.forest_mask,
                        'total_area_ha': (image.shape[0] * image.shape[1] * scale_factor ** 2) / 10000,
                        'forest_area_ha': ai_result.area_ha,
                        'coverage_percent': ai_result.coverage_percent,
                        'detection_method': ai_result.detection_method,
                        'confidence_score': ai_result.confidence_score,
                        'forest_types': ai_result.forest_types,
                        'canopy_density': ai_result.canopy_density,
                        'vegetation_indices': ai_result.vegetation_indices,
                        'ai_detection': True
                    }
            except Exception as e:
                logging.warning(f"AI detection failed, falling back to traditional: {e}")
        
        # Fallback to traditional detection
        result = self.detect_area(image, scale_factor, forest_type)
        
        # Add default values for AI-specific fields
        result.update({
            'detection_method': f'Traditional ({forest_type or "auto"})',
            'confidence_score': 0.7 if result['forest_area_ha'] > 0 else 0.0,
            'forest_types': {forest_type: 100.0} if forest_type else {},
            'canopy_density': 0.0,
            'vegetation_indices': {},
            'ai_detection': False
        })
        
        return result

# Create a singleton instance
forest_detector = AdvancedForestDetector()