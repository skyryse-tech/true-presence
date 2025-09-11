"""
Face processing worker for the True Presence Attendance System
Handles face detection and recognition using advanced ML models
"""

import logging
import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
import base64
import json
from io import BytesIO
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .config import FaceDetectionConfig
from .detection_service import FaceDetectionService, DetectedFace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceProcessor:
    """
    Main face processing class that orchestrates detection, quality assessment,
    and embedding extraction for the attendance system
    """
    
    def __init__(self, config: Optional[FaceDetectionConfig] = None):
        """
        Initialize Face Processor with configuration
        
        Args:
            config: Face detection configuration (loads from env if None)
        """
        self.config = config or FaceDetectionConfig.from_env()
        self.detection_service = FaceDetectionService(self.config)
        
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        logger.info(f"FaceProcessor initialized with {self.config.detector_backend.value} detector")

    
    def preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Preprocess image from bytes to numpy array
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Preprocessed image as numpy array or None if failed
        """
        try:
            image = Image.open(BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_array = np.array(image)
            
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            if image_array.size == 0:
                logger.warning("Empty image provided")
                return None
            
            height, width = image_array.shape[:2]
            if height < self.config.min_face_size or width < self.config.min_face_size:
                logger.warning(f"Image too small: {width}x{height}")
                return None
            
            logger.debug(f"Image preprocessed: shape {image_array.shape}")
            return image_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Complete face processing pipeline
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processing results with detected faces, quality metrics, and embeddings
        """
        try:
            image = self.preprocess_image(image_data)
            if image is None:
                return {
                    "success": False,
                    "error": "Image preprocessing failed",
                    "faces": []
                }
            
            detected_faces = self.detection_service.detect_faces(image)
            
            if not detected_faces:
                return {
                    "success": True,
                    "message": "No faces detected",
                    "faces": [],
                    "total_faces": 0
                }
            
            processed_faces = []
            for i, face in enumerate(detected_faces):
                try:
                    processed_face = self._process_single_face(face, i)
                    if processed_face:
                        processed_faces.append(processed_face)
                except Exception as e:
                    logger.error(f"Failed to process face {i}: {e}")
                    continue
            
            return {
                "success": True,
                "faces_detected": len(detected_faces),
                "faces_processed": len(processed_faces),
                "faces": processed_faces,
                "detection_config": {
                    "model": self.config.recognition_model.value,
                    "detector": self.config.detector_backend.value,
                    "quality_check": self.config.enable_quality_check,
                    "anti_spoofing": self.config.enable_anti_spoofing
                }
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "faces": []
            }
    
    def _process_single_face(self, detected_face: DetectedFace, face_index: int) -> Optional[Dict[str, Any]]:
        """
        Process a single detected face
        
        Args:
            detected_face: DetectedFace object from detection service
            face_index: Index of the face for identification
            
        Returns:
            Processed face data or None if processing failed
        """
        try:
            embedding = None
            if self.config.extract_embeddings:
                embedding = self.detection_service.get_embedding(detected_face.cropped_face)
            
            face_base64 = None
            if self.config.return_face_crops:
                _, buffer = cv2.imencode('.jpg', detected_face.cropped_face)
                face_base64 = base64.b64encode(buffer).decode('utf-8')
            
            processed_face = {
                "face_id": face_index,
                "bbox": {
                    "x": detected_face.bbox.x,
                    "y": detected_face.bbox.y,
                    "width": detected_face.bbox.width,
                    "height": detected_face.bbox.height
                },
                "confidence": detected_face.confidence,
                "quality": {
                    "brightness": detected_face.quality.brightness,
                    "blur_score": detected_face.quality.blur_score,
                    "sharpness": detected_face.quality.sharpness,
                    "quality_score": detected_face.quality.quality_score,
                    "is_good_quality": detected_face.quality.is_good_quality
                },
                "is_live": detected_face.is_live,
                "landmarks": None,
                "embedding": embedding.tolist() if embedding is not None else None,
                "embedding_size": len(embedding) if embedding is not None else 0,
                "face_crop_base64": face_base64
            }
            
            if detected_face.landmarks:
                processed_face["landmarks"] = {
                    "left_eye": detected_face.landmarks.left_eye,
                    "right_eye": detected_face.landmarks.right_eye,
                    "nose": detected_face.landmarks.nose,
                    "mouth_left": detected_face.landmarks.mouth_left,
                    "mouth_right": detected_face.landmarks.mouth_right
                }
            
            return processed_face
            
        except Exception as e:
            logger.error(f"Single face processing failed: {e}")
            return None

    
    async def process_image_async(self, image_data: bytes) -> Dict[str, Any]:
        """
        Asynchronous face processing
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processing results
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self.process_image, image_data)
        return result
    
    def compare_faces(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Dict[str, Any]:
        """
        Compare two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Dictionary with similarity score and match result
        """
        return self.detection_service.compare_embeddings(embedding1, embedding2)
    
    def validate_face_for_attendance(self, face_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a detected face is suitable for attendance recording
        
        Args:
            face_data: Processed face data from process_image
            
        Returns:
            Validation result with detailed feedback
        """
        try:
            validation_result = {
                "is_valid": True,
                "reasons": [],
                "confidence": face_data.get("confidence", 0.0),
                "quality_score": face_data.get("quality", {}).get("quality_score", 0.0)
            }
            
            # Check detection confidence
            if face_data.get("confidence", 0.0) < self.config.min_detection_confidence:
                validation_result["is_valid"] = False
                validation_result["reasons"].append(
                    f"Low detection confidence: {face_data.get('confidence', 0.0):.2f}"
                )
            
            if self.config.enable_quality_check:
                quality = face_data.get("quality", {})
                if not quality.get("is_good_quality", False):
                    validation_result["is_valid"] = False
                    validation_result["reasons"].append(
                        f"Poor image quality: score {quality.get('quality_score', 0.0):.2f}"
                    )
            
            if self.config.enable_anti_spoofing:
                if not face_data.get("is_live", True):
                    validation_result["is_valid"] = False
                    validation_result["reasons"].append("Failed liveness detection")
            
            if self.config.extract_embeddings and not face_data.get("embedding"):
                validation_result["is_valid"] = False
                validation_result["reasons"].append("Failed to extract face embedding")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Face validation failed: {e}")
            return {
                "is_valid": False,
                "reasons": [f"Validation error: {str(e)}"],
                "confidence": 0.0,
                "quality_score": 0.0
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the face processing system
        
        Returns:
            System information dictionary
        """
        return {
            "processor_config": {
                "recognition_model": self.config.recognition_model.value,
                "detector_backend": self.config.detector_backend.value,
                "target_size": self.config.target_size,
                "max_faces": self.config.max_faces_per_image,
                "min_face_size": self.config.min_face_size,
                "quality_check_enabled": self.config.enable_quality_check,
                "anti_spoofing_enabled": self.config.enable_anti_spoofing,
                "embedding_extraction": self.config.extract_embeddings
            },
            "quality_thresholds": {
                "min_detection_confidence": self.config.min_detection_confidence,
                "recognition_threshold": self.config.recognition_threshold,
                "min_quality_score": self.config.min_quality_score,
                "blur_threshold": self.config.blur_threshold,
                "brightness_range": self.config.brightness_range
            },
            "available_models": [model.value for model in self.config.recognition_model.__class__],
            "available_detectors": [detector.value for detector in self.config.detector_backend.__class__],
            "system_status": "operational"
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update processor configuration
        
        Args:
            new_config: Dictionary with new configuration values
            
        Returns:
            Updated configuration status
        """
        try:
            updated_fields = []
            
            if "min_detection_confidence" in new_config:
                self.config.min_detection_confidence = float(new_config["min_detection_confidence"])
                updated_fields.append("min_detection_confidence")
            
            if "recognition_threshold" in new_config:
                self.config.recognition_threshold = float(new_config["recognition_threshold"])
                updated_fields.append("recognition_threshold")
            
            if "enable_quality_check" in new_config:
                self.config.enable_quality_check = bool(new_config["enable_quality_check"])
                updated_fields.append("enable_quality_check")
            
            if "enable_anti_spoofing" in new_config:
                self.config.enable_anti_spoofing = bool(new_config["enable_anti_spoofing"])
                updated_fields.append("enable_anti_spoofing")
            
            logger.info(f"Configuration updated: {updated_fields}")
            
            return {
                "success": True,
                "updated_fields": updated_fields,
                "current_config": self.get_system_info()["processor_config"]
            }
            
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Compatibility layer for legacy code
class LegacyFaceProcessor:
    """
    Legacy compatibility layer for existing code that uses the old interface
    """
    
    def __init__(self):
        """Initialize with default configuration"""
        self.processor = FaceProcessor()
        logger.info("Legacy FaceProcessor initialized")
    
    def process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Legacy method for processing video frames
        
        Args:
            frame: Input image frame from camera
            
        Returns:
            List of detected faces in legacy format
        """
        try:
            # Convert frame to bytes for processing
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()
            
            # Process using new pipeline
            result = self.processor.process_image(image_bytes)
            
            if not result.get("success", False):
                return []
            
            # Convert to legacy format
            legacy_results = []
            for face in result.get("faces", []):
                bbox = face.get("bbox", {})
                legacy_face = {
                    "bbox": [bbox.get("x", 0), bbox.get("y", 0), 
                            bbox.get("width", 0), bbox.get("height", 0)],
                    "confidence": face.get("confidence", 0.0),
                    "is_live": face.get("is_live", False),
                    "embedding": face.get("embedding")
                }
                legacy_results.append(legacy_face)
            
            return legacy_results
            
        except Exception as e:
            logger.error(f"Legacy frame processing failed: {e}")
            return []
    
    def get_embedding(self, face_crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Legacy method for getting face embeddings
        
        Args:
            face_crop: Cropped face image
            
        Returns:
            Face embedding vector or None if failed
        """
        try:
            embedding = self.processor.detection_service.get_embedding(face_crop)
            return embedding
        except Exception as e:
            logger.error(f"Legacy embedding extraction failed: {e}")
            return None
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray, 
                          threshold: float = 0.6) -> Dict[str, Any]:
        """
        Legacy method for comparing embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            threshold: Similarity threshold for matching
            
        Returns:
            Dictionary with similarity score and match status
        """
        try:
            result = self.processor.compare_faces(embedding1, embedding2)
            # Convert to legacy format
            return {
                "similarity": result.get("similarity", 0.0),
                "is_match": result.get("similarity", 0.0) > threshold
            }
        except Exception as e:
            logger.error(f"Legacy embedding comparison failed: {e}")
            return {"similarity": 0.0, "is_match": False}

# Global face processor instances
_face_processor = None
_legacy_processor = None

def get_face_processor() -> FaceProcessor:
    """Get the global face processor instance (singleton pattern)"""
    global _face_processor
    if _face_processor is None:
        _face_processor = FaceProcessor()
    return _face_processor

def get_legacy_processor() -> LegacyFaceProcessor:
    """Get the global legacy processor instance (singleton pattern)"""
    global _legacy_processor
    if _legacy_processor is None:
        _legacy_processor = LegacyFaceProcessor()
    return _legacy_processor

def reset_face_processor(config: Optional[FaceDetectionConfig] = None) -> FaceProcessor:
    """Reset the global face processor with new configuration"""
    global _face_processor
    _face_processor = FaceProcessor(config)
    return _face_processor

# For backward compatibility with existing imports
FaceProcessor_Legacy = LegacyFaceProcessor

# Example usage and testing
if __name__ == '__main__':
    # This block will only run when you execute `python face_processor.py`
    import sys
    import os
    
    print("Testing Face Processing System...")
    
    try:
        # Initialize the processor
        processor = FaceProcessor()
        
        # Get system info
        info = processor.get_system_info()
        print(f"\nSystem Configuration:")
        print(f"- Recognition Model: {info['processor_config']['recognition_model']}")
        print(f"- Detector Backend: {info['processor_config']['detector_backend']}")
        print(f"- Quality Check: {info['processor_config']['quality_check_enabled']}")
        print(f"- Anti-spoofing: {info['processor_config']['anti_spoofing_enabled']}")
        
        # Test with a dummy image if available
        test_image_path = "test_image.jpg"
        if os.path.exists(test_image_path):
            with open(test_image_path, "rb") as f:
                image_data = f.read()
            
            result = processor.process_image(image_data)
            print(f"\nProcessing Result:")
            print(f"- Success: {result.get('success', False)}")
            print(f"- Faces Detected: {result.get('faces_detected', 0)}")
            print(f"- Faces Processed: {result.get('faces_processed', 0)}")
            
            for i, face in enumerate(result.get('faces', [])):
                print(f"\nFace {i+1}:")
                print(f"  - Confidence: {face.get('confidence', 0.0):.3f}")
                print(f"  - Quality Score: {face.get('quality', {}).get('quality_score', 0.0):.3f}")
                print(f"  - Is Live: {face.get('is_live', False)}")
                print(f"  - Has Embedding: {face.get('embedding') is not None}")
        else:
            print(f"\nTest image '{test_image_path}' not found.")
            print("Create a test image to run the full test.")
        
        print("\nFace Processing System test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)