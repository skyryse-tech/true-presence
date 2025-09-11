"""
Advanced Face Detection Service
Handles face detection with multiple backends, quality assessment, and error handling
"""
import cv2
import numpy as np
import logging
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from deepface import DeepFace
from .config import FaceDetectionConfig, DetectorBackend, RecognitionModel

logger = logging.getLogger(__name__)

@dataclass
class BoundingBox:
    """Face bounding box with confidence"""
    x: int
    y: int
    width: int
    height: int
    confidence: float

@dataclass
class FaceLandmarks:
    """Face landmarks (eyes, nose, mouth)"""
    left_eye: Tuple[float, float]
    right_eye: Tuple[float, float]
    nose: Tuple[float, float]
    mouth_left: Tuple[float, float]
    mouth_right: Tuple[float, float]

@dataclass
class FaceQuality:
    """Face quality metrics"""
    brightness: float
    blur_score: float
    sharpness: float
    pose_angle: float
    quality_score: float
    is_good_quality: bool

@dataclass
class DetectedFace:
    """Complete face detection result"""
    bbox: BoundingBox
    landmarks: Optional[FaceLandmarks]
    quality: FaceQuality
    cropped_face: np.ndarray
    is_live: bool
    embedding: Optional[np.ndarray]
    confidence: float

class FaceDetector(ABC):
    """Abstract base class for face detectors"""
    
    @abstractmethod
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if detector is available"""
        pass

class MTCNNDetector(FaceDetector):
    """MTCNN face detector"""
    
    def __init__(self):
        try:
            from mtcnn import MTCNN
            self.detector = MTCNN()
            self._available = True
        except ImportError as e:
            logger.error(f"MTCNN not available: {e}")
            self._available = False
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        
        try:
            results = self.detector.detect_faces(image)
            return results
        except Exception as e:
            logger.error(f"MTCNN detection failed: {e}")
            return []
    
    def is_available(self) -> bool:
        return self._available

class RetinaFaceDetector(FaceDetector):
    """RetinaFace detector"""
    
    def __init__(self):
        try:
            from retinaface import RetinaFace
            self.detector = RetinaFace
            self._available = True
        except ImportError as e:
            logger.error(f"RetinaFace not available: {e}")
            self._available = False
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        
        try:
            temp_path = "/tmp/temp_face_detection.jpg"
            cv2.imwrite(temp_path, image)
            results = self.detector.detect_faces(temp_path)
            
            faces = []
            for face_key, face_data in results.items():
                if isinstance(face_data, dict):
                    bbox = face_data.get('facial_area', [0, 0, 0, 0])
                    confidence = face_data.get('score', 0.0)
                    landmarks = face_data.get('landmarks', {})
                    
                    faces.append({
                        'box': [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]],
                        'confidence': confidence,
                        'keypoints': landmarks
                    })
            
            return faces
        except Exception as e:
            logger.error(f"RetinaFace detection failed: {e}")
            return []
    
    def is_available(self) -> bool:
        return self._available

class DeepFaceDetector(FaceDetector):
    """DeepFace detector (uses multiple backends)"""
    
    def __init__(self, backend: str = 'retinaface'):
        self.backend = backend
        self._available = True
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        try:
            faces = DeepFace.extract_faces(
                img_path=image,
                detector_backend=self.backend,
                enforce_detection=False,
                align=True,
                target_size=(224, 224)
            )
            
            results = []
            for i, face in enumerate(faces):
                if face is not None:
                    h, w = image.shape[:2]
                    face_size = min(h, w) // 2
                    x = (w - face_size) // 2
                    y = (h - face_size) // 2
                    
                    results.append({
                        'box': [x, y, face_size, face_size],
                        'confidence': 0.9,
                        'keypoints': {}
                    })
            
            return results
        except Exception as e:
            logger.error(f"DeepFace detection failed: {e}")
            return []
    
    def is_available(self) -> bool:
        return self._available

class FaceQualityAssessment:
    """Assess face image quality"""
    
    @staticmethod
    def calculate_brightness(image: np.ndarray) -> float:
        """Calculate image brightness"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)
    
    @staticmethod
    def calculate_blur_score(image: np.ndarray) -> float:
        """Calculate blur score using Laplacian variance"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    @staticmethod
    def calculate_sharpness(image: np.ndarray) -> float:
        """Calculate image sharpness"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sharpness = np.sqrt(sobel_x**2 + sobel_y**2).mean()
        return sharpness
    
    @classmethod
    def assess_quality(cls, face_crop: np.ndarray, config: FaceDetectionConfig) -> FaceQuality:
        """Comprehensive face quality assessment"""
        if face_crop.size == 0:
            return FaceQuality(0, 0, 0, 0, 0, False)
        
        brightness = cls.calculate_brightness(face_crop)
        blur_score = cls.calculate_blur_score(face_crop)
        sharpness = cls.calculate_sharpness(face_crop)
        
        # Simple pose estimation (placeholder)
        pose_angle = 0.0
        
        # Calculate overall quality score
        brightness_ok = config.brightness_range[0] <= brightness <= config.brightness_range[1]
        blur_ok = blur_score > config.blur_threshold
        
        quality_score = 0.0
        if brightness_ok:
            quality_score += 0.3
        if blur_ok:
            quality_score += 0.4
        quality_score += min(sharpness / 100.0, 0.3)  # Normalize sharpness
        
        is_good_quality = quality_score >= config.min_quality_score
        
        return FaceQuality(
            brightness=brightness,
            blur_score=blur_score,
            sharpness=sharpness,
            pose_angle=pose_angle,
            quality_score=quality_score,
            is_good_quality=is_good_quality
        )

class AntiSpoofingDetector:
    """Anti-spoofing/liveness detection"""
    
    def __init__(self, config: FaceDetectionConfig):
        self.config = config
        # In a real implementation, you would load a trained anti-spoofing model here
        # self.model = load_anti_spoofing_model()
    
    def is_live(self, face_crop: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if face is live or spoofed
        
        Returns:
            Tuple[bool, float]: (is_live, confidence_score)
        """
        if not self.config.enable_anti_spoofing:
            return True, 1.0
        
        # Placeholder implementation
        # In a real system, you would use a trained CNN model
        
        # Simple checks for basic spoofing detection
        if face_crop.size == 0:
            return False, 0.0
        
        # Check for image variation (printed photos tend to have less variation)
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        
        # Check for color distribution
        color_variance = np.var(face_crop, axis=(0, 1))
        color_score = np.mean(color_variance)
        
        # Simple scoring (replace with actual model inference)
        confidence = min((variance / 1000.0) + (color_score / 1000.0), 1.0)
        is_live = confidence > self.config.anti_spoofing_threshold
        
        return is_live, confidence

class FaceDetectionService:
    """Main face detection service"""
    
    def __init__(self, config: Optional[FaceDetectionConfig] = None):
        self.config = config or FaceDetectionConfig.from_env()
        self.detector = self._initialize_detector()
        self.quality_assessor = FaceQualityAssessment()
        self.anti_spoofing = AntiSpoofingDetector(self.config)
        
        logger.info(f"Face detection service initialized with {self.config.detector_backend.value}")
    
    def _initialize_detector(self) -> FaceDetector:
        """Initialize the face detector based on configuration"""
        if self.config.detector_backend == DetectorBackend.MTCNN:
            return MTCNNDetector()
        elif self.config.detector_backend == DetectorBackend.RETINAFACE:
            detector = RetinaFaceDetector()
            if not detector.is_available():
                logger.warning("RetinaFace not available, falling back to MTCNN")
                return MTCNNDetector()
            return detector
        else:
            # Default to DeepFace with specified backend
            return DeepFaceDetector(self.config.detector_backend.value)
    
    def _extract_face_crop(self, image: np.ndarray, bbox: BoundingBox) -> np.ndarray:
        """Extract face crop from image"""
        x, y, w, h = bbox.x, bbox.y, bbox.width, bbox.height
        
        # Ensure coordinates are within image bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        if w <= 0 or h <= 0:
            return np.array([])
        
        face_crop = image[y:y+h, x:x+w]
        
        # Resize to target size if needed
        if self.config.target_size:
            face_crop = cv2.resize(face_crop, self.config.target_size)
        
        return face_crop
    
    def _parse_detection_result(self, detection: Dict[str, Any]) -> Tuple[BoundingBox, Optional[FaceLandmarks]]:
        """Parse detection result to standard format"""
        # Extract bounding box
        box = detection.get('box', [0, 0, 0, 0])
        confidence = detection.get('confidence', 0.0)
        bbox = BoundingBox(
            x=int(box[0]),
            y=int(box[1]),
            width=int(box[2]),
            height=int(box[3]),
            confidence=confidence
        )
        
        # Extract landmarks if available
        landmarks = None
        keypoints = detection.get('keypoints', {})
        if keypoints:
            landmarks = FaceLandmarks(
                left_eye=keypoints.get('left_eye', (0, 0)),
                right_eye=keypoints.get('right_eye', (0, 0)),
                nose=keypoints.get('nose', (0, 0)),
                mouth_left=keypoints.get('mouth_left', (0, 0)),
                mouth_right=keypoints.get('mouth_right', (0, 0))
            )
        
        return bbox, landmarks
    
    def detect_faces(self, image: np.ndarray) -> List[DetectedFace]:
        """
        Detect faces in image with full pipeline
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected faces with all attributes
        """
        if image is None or image.size == 0:
            logger.warning("Empty image provided")
            return []
        
        start_time = time.time()
        
        try:
            # Step 1: Face Detection
            detections = self.detector.detect_faces(image)
            
            if not detections:
                logger.info("No faces detected")
                return []
            
            detected_faces = []
            
            for detection in detections[:self.config.max_faces_per_image]:
                # Parse detection result
                bbox, landmarks = self._parse_detection_result(detection)
                
                # Filter by confidence
                if bbox.confidence < self.config.min_detection_confidence:
                    continue
                
                # Filter by face size
                if bbox.width < self.config.min_face_size or bbox.height < self.config.min_face_size:
                    continue
                
                # Extract face crop
                face_crop = self._extract_face_crop(image, bbox)
                if face_crop.size == 0:
                    continue
                
                # Step 2: Quality Assessment
                quality = self.quality_assessor.assess_quality(face_crop, self.config)
                
                # Skip low quality faces if quality check is enabled
                if self.config.enable_quality_check and not quality.is_good_quality:
                    logger.info(f"Face quality too low: {quality.quality_score}")
                    continue
                
                # Step 3: Anti-spoofing Detection
                is_live, spoofing_confidence = self.anti_spoofing.is_live(face_crop)
                
                # Step 4: Create detected face object
                detected_face = DetectedFace(
                    bbox=bbox,
                    landmarks=landmarks,
                    quality=quality,
                    cropped_face=face_crop,
                    is_live=is_live,
                    embedding=None,  # Will be computed separately if needed
                    confidence=bbox.confidence
                )
                
                detected_faces.append(detected_face)
            
            processing_time = time.time() - start_time
            logger.info(f"Detected {len(detected_faces)} faces in {processing_time:.2f}s")
            
            return detected_faces
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def get_embedding(self, face_crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding using configured recognition model
        
        Args:
            face_crop: Cropped face image
            
        Returns:
            Face embedding vector or None if failed
        """
        try:
            embedding_result = DeepFace.represent(
                img_path=face_crop,
                model_name=self.config.recognition_model.value,
                enforce_detection=False,
                detector_backend='skip'  # Skip detection since we already have cropped face
            )
            
            if embedding_result and len(embedding_result) > 0:
                embedding = np.array(embedding_result[0]["embedding"])
                logger.debug(f"Generated embedding of size {len(embedding)}")
                return embedding
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
        
        return None
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Dict[str, Any]:
        """
        Compare two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Dictionary with similarity score and match result
        """
        if embedding1 is None or embedding2 is None:
            return {"similarity": 0.0, "is_match": False, "distance": float('inf')}
        
        try:
            # Convert to numpy arrays if needed
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            # Calculate cosine similarity
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return {"similarity": 0.0, "is_match": False, "distance": float('inf')}
            
            cosine_similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            euclidean_distance = np.linalg.norm(embedding1 - embedding2)
            
            is_match = cosine_similarity > self.config.recognition_threshold
            
            return {
                "similarity": float(cosine_similarity),
                "distance": float(euclidean_distance),
                "is_match": bool(is_match),
                "threshold": self.config.recognition_threshold
            }
            
        except Exception as e:
            logger.error(f"Embedding comparison failed: {e}")
            return {"similarity": 0.0, "is_match": False, "distance": float('inf')}
