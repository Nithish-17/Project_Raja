"""
OCR Accuracy Improvement with Image Preprocessing
Enhances OCR quality through advanced preprocessing techniques
"""
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None
    np = None

from PIL import Image
from typing import Tuple, Optional, Union
import io

from utils import get_logger

logger = get_logger("ocr.preprocessing")


class OCRPreprocessor:
    """Advanced image preprocessing for OCR"""
    
    def __init__(self):
        """Initialize preprocessor"""
        self.quality_threshold = 0.5
        logger.info("OCR Preprocessor initialized")
    
    def preprocess(self, image_path: str) -> Tuple[Optional['np.ndarray'], float]:
        """
        Preprocess image for OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (preprocessed_image, quality_score)
        """
        if not HAS_CV2:
            logger.warning("OpenCV not available; skipping preprocessing")
            return None, 0.0
        
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None, 0.0
            
            # Store original for comparison
            original = image.copy()
            
            # Apply preprocessing steps
            image = self._convert_to_grayscale(image)
            image = self._denoise(image)
            image = self._apply_thresholding(image)
            image = self._deskew(image)
            image = self._enhance_contrast(image)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(original, image)
            
            if quality_score < self.quality_threshold:
                logger.warning(f"Low OCR quality score: {quality_score:.2f} for {image_path}")
            
            logger.info(f"Image preprocessed: quality_score={quality_score:.2f}")
            
            return image, quality_score
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return None, 0.0
    
    def preprocess_from_bytes(self, image_bytes: bytes) -> Tuple[Optional['np.ndarray'], float]:
        """Preprocess image from bytes"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image from bytes")
                return None, 0.0
            
            # Store original
            original = image.copy()
            
            # Apply preprocessing
            image = self._convert_to_grayscale(image)
            image = self._denoise(image)
            image = self._apply_thresholding(image)
            image = self._deskew(image)
            image = self._enhance_contrast(image)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(original, image)
            
            return image, quality_score
            
        except Exception as e:
            logger.error(f"Error preprocessing image from bytes: {str(e)}")
            return None, 0.0
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        # Use bilateral filter for edge-preserving denoising
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        return denoised
    
    def _apply_thresholding(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding"""
        # Adaptive thresholding for varying lighting
        thresholded = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        return thresholded
    
    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Deskew/correct image rotation"""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Fit rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Correct angle
            if angle < -45:
                angle = angle + 90
            
            # Rotate if needed
            if abs(angle) > 1:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                image = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
            
            return image
            
        except Exception as e:
            logger.debug(f"Deskew error: {str(e)}")
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE"""
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
            return enhanced
        except Exception as e:
            logger.debug(f"Contrast enhancement error: {str(e)}")
            return image
    
    def _calculate_quality_score(self, original: np.ndarray, processed: np.ndarray) -> float:
        """Calculate quality score of preprocessing"""
        try:
            # Calculate Laplacian variance (sharpness indicator)
            laplacian_var = cv2.Laplacian(processed, cv2.CV_64F).var()
            
            # Normalize to 0-100 scale
            quality_score = min(100.0, laplacian_var / 500.0 * 100.0)
            
            return quality_score
            
        except Exception as e:
            logger.debug(f"Quality calculation error: {str(e)}")
            return 50.0


# Global preprocessor instance
ocr_preprocessor = OCRPreprocessor()
