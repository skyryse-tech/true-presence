"""
Face Detection Configuration
"""
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class DetectorBackend(Enum):
    """Supported face detection backends"""
    OPENCV = "opencv"
    MTCNN = "mtcnn"
    RETINAFACE = "retinaface"
    MEDIAPIPE = "mediapipe"
    YOLO = "yolo"

class RecognitionModel(Enum):
    """Supported face recognition models"""
    ARCFACE = "ArcFace"
    FACENET = "Facenet"
    FACENET512 = "Facenet512"
    VGG_FACE = "VGG-Face"
    OPENFACE = "OpenFace"

@dataclass
class FaceDetectionConfig:
    """Configuration for face detection system"""
    
    # Detection settings
    detector_backend: DetectorBackend = DetectorBackend.RETINAFACE
    min_detection_confidence: float = 0.9
    max_faces_per_image: int = 10
    min_face_size: int = 50
    
    # Recognition settings
    recognition_model: RecognitionModel = RecognitionModel.ARCFACE
    recognition_threshold: float = 0.6
    embedding_size: int = 512
    
    # Anti-spoofing settings
    enable_anti_spoofing: bool = True
    anti_spoofing_threshold: float = 0.95
    
    # Quality assessment
    enable_quality_check: bool = True
    min_quality_score: float = 0.7
    blur_threshold: float = 100.0
    brightness_range: tuple = (50, 200)
    
    # Performance settings
    batch_size: int = 32
    gpu_device: int = 0
    enable_gpu: bool = True
    
    # Image preprocessing
    target_size: tuple = (224, 224)
    normalize: bool = True
    align_faces: bool = True
    
    @classmethod
    def from_env(cls) -> 'FaceDetectionConfig':
        """Create configuration from environment variables"""
        return cls(
            detector_backend=DetectorBackend(os.getenv('DETECTOR_BACKEND', 'retinaface')),
            min_detection_confidence=float(os.getenv('FACE_DETECTION_THRESHOLD', '0.9')),
            recognition_threshold=float(os.getenv('FACE_RECOGNITION_THRESHOLD', '0.6')),
            anti_spoofing_threshold=float(os.getenv('ANTI_SPOOFING_THRESHOLD', '0.95')),
            batch_size=int(os.getenv('BATCH_SIZE', '32')),
            gpu_device=int(os.getenv('GPU_DEVICE', '0')),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'detector_backend': self.detector_backend.value,
            'min_detection_confidence': self.min_detection_confidence,
            'max_faces_per_image': self.max_faces_per_image,
            'min_face_size': self.min_face_size,
            'recognition_model': self.recognition_model.value,
            'recognition_threshold': self.recognition_threshold,
            'embedding_size': self.embedding_size,
            'enable_anti_spoofing': self.enable_anti_spoofing,
            'anti_spoofing_threshold': self.anti_spoofing_threshold,
            'enable_quality_check': self.enable_quality_check,
            'min_quality_score': self.min_quality_score,
            'blur_threshold': self.blur_threshold,
            'brightness_range': self.brightness_range,
            'batch_size': self.batch_size,
            'gpu_device': self.gpu_device,
            'enable_gpu': self.enable_gpu,
            'target_size': self.target_size,
            'normalize': self.normalize,
            'align_faces': self.align_faces,
        }
