"""
AI Workers Package for True Presence Attendance System

This package contains:
- Face detection and recognition services
- Configuration management
- Worker implementations
- Detection algorithms

Main Components:
- FaceProcessor: Main processing class with modern API
- FaceDetectionService: Core detection service with multiple backends
- FaceDetectionConfig: Configuration management
- LegacyFaceProcessor: Backward compatibility layer
"""

from .face_processor import (
    FaceProcessor,
    LegacyFaceProcessor, 
    get_face_processor,
    get_legacy_processor,
    reset_face_processor
)

from .detection_service import (
    FaceDetectionService,
    DetectedFace,
    BoundingBox,
    FaceLandmarks,
    FaceQuality
)

from .config import (
    FaceDetectionConfig,
    DetectorBackend,
    RecognitionModel
)

__version__ = "1.0.0"
__author__ = "True Presence Team"

# Module exports
__all__ = [
    # Main processor classes
    "FaceProcessor",
    "LegacyFaceProcessor",
    "FaceDetectionService",
    
    # Data structures
    "DetectedFace",
    "BoundingBox", 
    "FaceLandmarks",
    "FaceQuality",
    
    # Configuration
    "FaceDetectionConfig",
    "DetectorBackend",
    "RecognitionModel",
    
    # Factory functions
    "get_face_processor",
    "get_legacy_processor",
    "reset_face_processor"
]

# Package metadata
__doc__ = """
True Presence AI Workers Package

Provides comprehensive face detection, quality assessment, and recognition
capabilities for the attendance system.

Example usage:
    >>> from ai_workers import get_face_processor
    >>> processor = get_face_processor()
    >>> result = processor.process_image(image_bytes)
    >>> print(f"Found {result['faces_detected']} faces")
"""
