"""
AI Worker Service for Face Recognition
Handles face detection, recognition, and liveness detection tasks
"""
import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional
import numpy as np
import cv2
from PIL import Image
import base64
import io
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from face_detection.detector import FaceDetector, FaceDetection
from face_recognition.recognizer import FaceRecognizer, FaceRecognition
from liveness_detection.detector import LivenessDetector, LivenessResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIWorker:
    """AI Worker for processing face recognition tasks"""
    
    def __init__(self):
        self.face_detector = FaceDetector(backend="mtcnn")
        self.face_recognizer = FaceRecognizer(backend="deepface")
        self.liveness_detector = LivenessDetector(method="blink_detection")
        logger.info("AI Worker initialized successfully")
    
    def process_image(self, image_data: str) -> np.ndarray:
        """Convert base64 image data to numpy array"""
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to numpy array (RGB)
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_array
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in an image"""
        try:
            detections = self.face_detector.detect_faces(image)
            
            results = []
            for detection in detections:
                results.append({
                    'bbox': detection.bbox,
                    'confidence': detection.confidence,
                    'face_quality': detection.face_quality,
                    'landmarks': detection.landmarks.tolist() if detection.landmarks is not None else None
                })
            
            return results
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def extract_face_embedding(self, image: np.ndarray, bbox: List[int]) -> Optional[np.ndarray]:
        """Extract face embedding from image and bounding box"""
        try:
            x, y, w, h = bbox
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return None
            
            embedding = self.face_recognizer.extract_embedding(face_region)
            return embedding.tolist()  # Convert to list for JSON serialization
        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            return None
    
    def enroll_face(self, image: np.ndarray, identity: str, bbox: List[int]) -> Dict[str, Any]:
        """Enroll a face in the recognition system"""
        try:
            x, y, w, h = bbox
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return {'success': False, 'error': 'Invalid face region'}
            
            success = self.face_recognizer.enroll_face(face_region, identity)
            
            if success:
                embedding = self.face_recognizer.extract_embedding(face_region)
                return {
                    'success': True,
                    'identity': identity,
                    'embedding': embedding.tolist(),
                    'face_quality': self.face_detector._calculate_face_quality(face_region)
                }
            else:
                return {'success': False, 'error': 'Failed to enroll face'}
        
        except Exception as e:
            logger.error(f"Error enrolling face: {e}")
            return {'success': False, 'error': str(e)}
    
    def recognize_face(self, image: np.ndarray, bbox: List[int], threshold: float = 0.6) -> Dict[str, Any]:
        """Recognize a face from the database"""
        try:
            x, y, w, h = bbox
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return {'success': False, 'error': 'Invalid face region'}
            
            recognition = self.face_recognizer.recognize_face(face_region, threshold)
            
            if recognition:
                return {
                    'success': True,
                    'identity': recognition.identity,
                    'confidence': recognition.confidence,
                    'distance': recognition.distance
                }
            else:
                return {'success': False, 'error': 'No matching face found'}
        
        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return {'success': False, 'error': str(e)}
    
    def detect_liveness(self, image: np.ndarray, bbox: List[int]) -> Dict[str, Any]:
        """Detect if a face is live (not a spoof)"""
        try:
            x, y, w, h = bbox
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return {'success': False, 'error': 'Invalid face region'}
            
            liveness_result = self.liveness_detector.detect_liveness(image, bbox)
            
            return {
                'success': True,
                'is_live': liveness_result.is_live,
                'confidence': liveness_result.confidence,
                'spoof_type': liveness_result.spoof_type,
                'quality_score': liveness_result.quality_score
            }
        
        except Exception as e:
            logger.error(f"Error detecting liveness: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_face_enrollment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process face enrollment task"""
        try:
            employee_id = task_data.get('employee_id')
            images = task_data.get('images', [])
            quality_check = task_data.get('quality_check', True)
            
            if not employee_id or not images:
                return {'success': False, 'error': 'Missing required fields'}
            
            if len(images) < 3:
                return {'success': False, 'error': 'At least 3 images required for enrollment'}
            
            enrollment_results = []
            
            for i, image_data in enumerate(images):
                try:
                    # Process image
                    image = self.process_image(image_data)
                    
                    # Detect faces
                    face_detections = self.detect_faces(image)
                    
                    if not face_detections:
                        enrollment_results.append({
                            'image_index': i,
                            'success': False,
                            'error': 'No face detected'
                        })
                        continue
                    
                    # Use the best quality face
                    best_detection = max(face_detections, key=lambda x: x['face_quality'])
                    
                    # Check quality if required
                    if quality_check and best_detection['face_quality'] < 0.5:
                        enrollment_results.append({
                            'image_index': i,
                            'success': False,
                            'error': 'Face quality too low'
                        })
                        continue
                    
                    # Enroll face
                    enrollment_result = self.enroll_face(
                        image, 
                        f"{employee_id}_{i}", 
                        best_detection['bbox']
                    )
                    
                    enrollment_results.append({
                        'image_index': i,
                        'success': enrollment_result['success'],
                        'face_quality': best_detection['face_quality'],
                        'error': enrollment_result.get('error')
                    })
                
                except Exception as e:
                    enrollment_results.append({
                        'image_index': i,
                        'success': False,
                        'error': str(e)
                    })
            
            # Check if at least one enrollment was successful
            successful_enrollments = [r for r in enrollment_results if r['success']]
            
            if len(successful_enrollments) >= 2:  # At least 2 out of 3 images
                return {
                    'success': True,
                    'employee_id': employee_id,
                    'enrollment_results': enrollment_results,
                    'total_images': len(images),
                    'successful_enrollments': len(successful_enrollments)
                }
            else:
                return {
                    'success': False,
                    'error': 'Insufficient successful enrollments',
                    'enrollment_results': enrollment_results
                }
        
        except Exception as e:
            logger.error(f"Error processing face enrollment: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_face_verification(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process face verification task"""
        try:
            image_data = task_data.get('image')
            camera_id = task_data.get('camera_id')
            location = task_data.get('location')
            threshold = task_data.get('threshold', 0.6)
            
            if not image_data:
                return {'success': False, 'error': 'Missing image data'}
            
            # Process image
            image = self.process_image(image_data)
            
            # Detect faces
            face_detections = self.detect_faces(image)
            
            if not face_detections:
                return {'success': False, 'error': 'No face detected'}
            
            # Use the best quality face
            best_detection = max(face_detections, key=lambda x: x['face_quality'])
            
            # Check face quality
            if best_detection['face_quality'] < 0.3:
                return {'success': False, 'error': 'Face quality too low'}
            
            # Detect liveness
            liveness_result = self.detect_liveness(image, best_detection['bbox'])
            
            if not liveness_result['success']:
                return {'success': False, 'error': 'Liveness detection failed'}
            
            if not liveness_result['is_live']:
                return {
                    'success': False, 
                    'error': 'Liveness check failed - possible spoof attack',
                    'liveness_confidence': liveness_result['confidence']
                }
            
            # Recognize face
            recognition_result = self.recognize_face(image, best_detection['bbox'], threshold)
            
            if not recognition_result['success']:
                return {
                    'success': False,
                    'error': 'Face not recognized',
                    'liveness_confidence': liveness_result['confidence']
                }
            
            return {
                'success': True,
                'identity': recognition_result['identity'],
                'confidence': recognition_result['confidence'],
                'face_quality': best_detection['face_quality'],
                'liveness_confidence': liveness_result['confidence'],
                'camera_id': camera_id,
                'location': location,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error processing face verification: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """Main function to run the AI worker"""
    worker = AIWorker()
    logger.info("AI Worker started successfully")
    
    # For now, we'll run a simple test
    # In production, this would connect to RabbitMQ or Redis for task processing
    try:
        while True:
            # Simulate processing tasks
            logger.info("AI Worker is running...")
            asyncio.sleep(60)  # Sleep for 1 minute
    except KeyboardInterrupt:
        logger.info("AI Worker stopped")

if __name__ == "__main__":
    main()
