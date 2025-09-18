"""
Face Detection Service using MTCNN and RetinaFace
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FaceDetection:
    """Face detection result"""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    landmarks: Optional[np.ndarray] = None
    face_quality: Optional[float] = None

class FaceDetector:
    """Face detection using multiple backends"""
    
    def __init__(self, backend: str = "mtcnn", confidence_threshold: float = 0.7):
        self.backend = backend
        self.confidence_threshold = confidence_threshold
        self.detector = None
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize the face detector based on backend"""
        try:
            if self.backend == "mtcnn":
                from mtcnn import MTCNN
                self.detector = MTCNN()
            elif self.backend == "retinaface":
                from retinaface import RetinaFace
                self.detector = RetinaFace
            elif self.backend == "opencv":
                # Use OpenCV Haar Cascades as fallback
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.detector = cv2.CascadeClassifier(cascade_path)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")
        except ImportError as e:
            logger.warning(f"Failed to import {self.backend}, falling back to OpenCV: {e}")
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cascade_path)
            self.backend = "opencv"
    
    def detect_faces(self, image: np.ndarray) -> List[FaceDetection]:
        """
        Detect faces in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of FaceDetection objects
        """
        if self.detector is None:
            return []
        
        try:
            if self.backend == "mtcnn":
                return self._detect_mtcnn(image)
            elif self.backend == "retinaface":
                return self._detect_retinaface(image)
            elif self.backend == "opencv":
                return self._detect_opencv(image)
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def _detect_mtcnn(self, image: np.ndarray) -> List[FaceDetection]:
        """Detect faces using MTCNN"""
        detections = self.detector.detect_faces(image)
        faces = []
        
        for detection in detections:
            if detection['confidence'] >= self.confidence_threshold:
                bbox = detection['box']
                # Convert to x, y, width, height format
                x, y, w, h = bbox
                faces.append(FaceDetection(
                    bbox=(x, y, w, h),
                    confidence=detection['confidence'],
                    landmarks=detection.get('keypoints'),
                    face_quality=self._calculate_face_quality(image, bbox)
                ))
        
        return faces
    
    def _detect_retinaface(self, image: np.ndarray) -> List[FaceDetection]:
        """Detect faces using RetinaFace"""
        detections = self.detector.detect_faces(image)
        faces = []
        
        for face in detections.values():
            if face['score'] >= self.confidence_threshold:
                bbox = face['facial_area']
                x, y, w, h = bbox
                faces.append(FaceDetection(
                    bbox=(x, y, w, h),
                    confidence=face['score'],
                    landmarks=face.get('landmarks'),
                    face_quality=self._calculate_face_quality(image, bbox)
                ))
        
        return faces
    
    def _detect_opencv(self, image: np.ndarray) -> List[FaceDetection]:
        """Detect faces using OpenCV Haar Cascades"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        faces_rect = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        faces = []
        for (x, y, w, h) in faces_rect:
            # OpenCV doesn't provide confidence, so we use a default value
            confidence = 0.8
            faces.append(FaceDetection(
                bbox=(x, y, w, h),
                confidence=confidence,
                face_quality=self._calculate_face_quality(image, (x, y, w, h))
            ))
        
        return faces
    
    def _calculate_face_quality(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> float:
        """Calculate face quality score based on various factors"""
        x, y, w, h = bbox
        
        # Extract face region
        face_region = image[y:y+h, x:x+w]
        if face_region.size == 0:
            return 0.0
        
        # Convert to grayscale for analysis
        if len(face_region.shape) == 3:
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray_face = face_region
        
        # Calculate quality metrics
        quality_score = 0.0
        
        # 1. Size factor (larger faces are generally better)
        size_factor = min(1.0, (w * h) / (100 * 100))
        quality_score += size_factor * 0.3
        
        # 2. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
        sharpness_factor = min(1.0, laplacian_var / 1000)
        quality_score += sharpness_factor * 0.4
        
        # 3. Brightness (avoid too dark or too bright)
        mean_brightness = np.mean(gray_face)
        brightness_factor = 1.0 - abs(mean_brightness - 127) / 127
        quality_score += brightness_factor * 0.3
        
        return min(1.0, quality_score)
    
    def extract_face(self, image: np.ndarray, detection: FaceDetection, 
                    target_size: Tuple[int, int] = (160, 160)) -> np.ndarray:
        """
        Extract face region from image
        
        Args:
            image: Input image
            detection: Face detection result
            target_size: Target size for extracted face
            
        Returns:
            Extracted face as numpy array
        """
        x, y, w, h = detection.bbox
        
        # Add some padding
        padding = 0.2
        pad_w = int(w * padding)
        pad_h = int(h * padding)
        
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(image.shape[1], x + w + pad_w)
        y2 = min(image.shape[0], y + h + pad_h)
        
        face_region = image[y1:y2, x1:x2]
        
        if face_region.size == 0:
            return np.array([])
        
        # Resize to target size
        face_resized = cv2.resize(face_region, target_size)
        
        return face_resized
