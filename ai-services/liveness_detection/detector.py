"""
Liveness Detection Service to prevent spoofing attacks
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LivenessResult:
    """Liveness detection result"""
    is_live: bool
    confidence: float
    spoof_type: Optional[str] = None
    quality_score: float = 0.0

class LivenessDetector:
    """Liveness detection using multiple methods"""
    
    def __init__(self, method: str = "blink_detection"):
        self.method = method
        self.eye_cascade = None
        self.face_cascade = None
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize OpenCV cascades for eye and face detection"""
        try:
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except Exception as e:
            logger.error(f"Failed to initialize cascades: {e}")
    
    def detect_liveness(self, image: np.ndarray, 
                       face_bbox: Optional[Tuple[int, int, int, int]] = None) -> LivenessResult:
        """
        Detect if the face in the image is live
        
        Args:
            image: Input image
            face_bbox: Optional face bounding box (x, y, w, h)
            
        Returns:
            LivenessResult object
        """
        try:
            if self.method == "blink_detection":
                return self._detect_blink_liveness(image, face_bbox)
            elif self.method == "texture_analysis":
                return self._detect_texture_liveness(image, face_bbox)
            elif self.method == "motion_analysis":
                return self._detect_motion_liveness(image, face_bbox)
            else:
                # Default to basic quality check
                return self._basic_quality_check(image, face_bbox)
        
        except Exception as e:
            logger.error(f"Liveness detection failed: {e}")
            return LivenessResult(is_live=False, confidence=0.0)
    
    def _detect_blink_liveness(self, image: np.ndarray, 
                              face_bbox: Optional[Tuple[int, int, int, int]]) -> LivenessResult:
        """Detect liveness based on eye detection and blink patterns"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # If face bbox is provided, use it; otherwise detect face
        if face_bbox:
            x, y, w, h = face_bbox
            face_region = gray[y:y+h, x:x+w]
        else:
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) == 0:
                return LivenessResult(is_live=False, confidence=0.0)
            x, y, w, h = faces[0]
            face_region = gray[y:y+h, x:x+w]
        
        # Detect eyes in the face region
        eyes = self.eye_cascade.detectMultiScale(face_region, 1.1, 3)
        
        # Basic liveness check: if eyes are detected, consider it live
        if len(eyes) >= 2:
            # Calculate eye quality
            eye_quality = self._calculate_eye_quality(face_region, eyes)
            confidence = min(0.9, 0.5 + eye_quality * 0.4)
            return LivenessResult(is_live=True, confidence=confidence)
        else:
            return LivenessResult(is_live=False, confidence=0.2)
    
    def _detect_texture_liveness(self, image: np.ndarray, 
                                face_bbox: Optional[Tuple[int, int, int, int]]) -> LivenessResult:
        """Detect liveness based on texture analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Extract face region
        if face_bbox:
            x, y, w, h = face_bbox
            face_region = gray[y:y+h, x:x+w]
        else:
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) == 0:
                return LivenessResult(is_live=False, confidence=0.0)
            x, y, w, h = faces[0]
            face_region = gray[y:y+h, x:x+w]
        
        # Calculate texture features
        texture_score = self._calculate_texture_features(face_region)
        
        # Higher texture variation indicates live face
        if texture_score > 0.3:
            confidence = min(0.8, texture_score)
            return LivenessResult(is_live=True, confidence=confidence)
        else:
            return LivenessResult(is_live=False, confidence=0.3)
    
    def _detect_motion_liveness(self, image: np.ndarray, 
                               face_bbox: Optional[Tuple[int, int, int, int]]) -> LivenessResult:
        """Detect liveness based on motion analysis (requires multiple frames)"""
        # This is a simplified version - in practice, you'd need multiple frames
        # For now, we'll do a basic quality check
        return self._basic_quality_check(image, face_bbox)
    
    def _basic_quality_check(self, image: np.ndarray, 
                            face_bbox: Optional[Tuple[int, int, int, int]]) -> LivenessResult:
        """Basic quality check for liveness detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Extract face region
        if face_bbox:
            x, y, w, h = face_bbox
            face_region = gray[y:y+h, x:x+w]
        else:
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) == 0:
                return LivenessResult(is_live=False, confidence=0.0)
            x, y, w, h = faces[0]
            face_region = gray[y:y+h, x:x+w]
        
        # Calculate quality metrics
        quality_score = self._calculate_face_quality(face_region)
        
        # Basic heuristic: higher quality = more likely to be live
        if quality_score > 0.5:
            confidence = min(0.7, quality_score)
            return LivenessResult(is_live=True, confidence=confidence)
        else:
            return LivenessResult(is_live=False, confidence=0.4)
    
    def _calculate_eye_quality(self, face_region: np.ndarray, eyes: List) -> float:
        """Calculate eye detection quality"""
        if len(eyes) < 2:
            return 0.0
        
        # Calculate eye size and position consistency
        eye_areas = []
        for (ex, ey, ew, eh) in eyes:
            eye_areas.append(ew * eh)
        
        # Check if eye sizes are consistent
        if len(eye_areas) >= 2:
            size_ratio = min(eye_areas) / max(eye_areas)
            return size_ratio
        
        return 0.5
    
    def _calculate_texture_features(self, face_region: np.ndarray) -> float:
        """Calculate texture features for liveness detection"""
        # Calculate Local Binary Pattern (LBP) variance
        # This is a simplified version
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(face_region, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(face_region, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate texture variation
        texture_variance = np.var(gradient_magnitude)
        
        # Normalize to 0-1 range
        normalized_variance = min(1.0, texture_variance / 1000)
        
        return normalized_variance
    
    def _calculate_face_quality(self, face_region: np.ndarray) -> float:
        """Calculate overall face quality"""
        if face_region.size == 0:
            return 0.0
        
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(face_region, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_var / 1000)
        
        # 2. Brightness (avoid too dark or too bright)
        mean_brightness = np.mean(face_region)
        brightness_score = 1.0 - abs(mean_brightness - 127) / 127
        
        # 3. Contrast
        contrast_score = np.std(face_region) / 255.0
        
        # Combine scores
        quality_score = (sharpness_score * 0.4 + brightness_score * 0.3 + contrast_score * 0.3)
        
        return quality_score
