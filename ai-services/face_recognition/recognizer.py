"""
Face Recognition Service using DeepFace and InsightFace
"""
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import logging
from dataclasses import dataclass
import cv2

logger = logging.getLogger(__name__)

@dataclass
class FaceRecognition:
    """Face recognition result"""
    identity: str
    confidence: float
    distance: float
    face_embedding: Optional[np.ndarray] = None

class FaceRecognizer:
    """Face recognition using multiple backends"""
    
    def __init__(self, backend: str = "deepface", model_name: str = "ArcFace"):
        self.backend = backend
        self.model_name = model_name
        self.model = None
        self.face_db = {}  # In-memory face database
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the face recognition model"""
        try:
            if self.backend == "deepface":
                from deepface import DeepFace
                self.model = DeepFace
            elif self.backend == "insightface":
                import insightface
                self.model = insightface.app.FaceAnalysis()
                self.model.prepare(ctx_id=0, det_size=(640, 640))
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")
        except ImportError as e:
            logger.error(f"Failed to import {self.backend}: {e}")
            raise
    
    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract face embedding from face image
        
        Args:
            face_image: Face image as numpy array
            
        Returns:
            Face embedding vector
        """
        try:
            if self.backend == "deepface":
                embedding = self.model.represent(
                    face_image,
                    model_name=self.model_name,
                    enforce_detection=False
                )[0]["embedding"]
                return np.array(embedding)
            
            elif self.backend == "insightface":
                faces = self.model.get(face_image)
                if len(faces) > 0:
                    return faces[0].embedding
                else:
                    raise ValueError("No face detected in image")
        
        except Exception as e:
            logger.error(f"Failed to extract embedding: {e}")
            raise
    
    def enroll_face(self, face_image: np.ndarray, identity: str) -> bool:
        """
        Enroll a face in the database
        
        Args:
            face_image: Face image as numpy array
            identity: Identity string (e.g., employee_id)
            
        Returns:
            True if enrollment successful
        """
        try:
            embedding = self.extract_embedding(face_image)
            self.face_db[identity] = embedding
            logger.info(f"Successfully enrolled face for identity: {identity}")
            return True
        except Exception as e:
            logger.error(f"Failed to enroll face for {identity}: {e}")
            return False
    
    def recognize_face(self, face_image: np.ndarray, 
                      threshold: float = 0.6) -> Optional[FaceRecognition]:
        """
        Recognize a face from the database
        
        Args:
            face_image: Face image as numpy array
            threshold: Recognition threshold
            
        Returns:
            FaceRecognition result or None if no match
        """
        try:
            query_embedding = self.extract_embedding(face_image)
            
            best_match = None
            best_distance = float('inf')
            
            for identity, stored_embedding in self.face_db.items():
                distance = self._calculate_distance(query_embedding, stored_embedding)
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = identity
            
            if best_match and best_distance <= threshold:
                confidence = 1.0 - (best_distance / threshold)
                return FaceRecognition(
                    identity=best_match,
                    confidence=confidence,
                    distance=best_distance,
                    face_embedding=query_embedding
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to recognize face: {e}")
            return None
    
    def _calculate_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine distance between two embeddings"""
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 1.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Convert to distance (0 = identical, 1 = completely different)
        distance = 1.0 - similarity
        
        return distance
    
    def verify_faces(self, face1: np.ndarray, face2: np.ndarray, 
                    threshold: float = 0.6) -> Tuple[bool, float]:
        """
        Verify if two faces belong to the same person
        
        Args:
            face1: First face image
            face2: Second face image
            threshold: Verification threshold
            
        Returns:
            Tuple of (is_same_person, confidence)
        """
        try:
            embedding1 = self.extract_embedding(face1)
            embedding2 = self.extract_embedding(face2)
            
            distance = self._calculate_distance(embedding1, embedding2)
            confidence = 1.0 - (distance / threshold)
            
            is_same = distance <= threshold
            
            return is_same, confidence
        
        except Exception as e:
            logger.error(f"Failed to verify faces: {e}")
            return False, 0.0
    
    def get_face_database_size(self) -> int:
        """Get the number of enrolled faces"""
        return len(self.face_db)
    
    def remove_identity(self, identity: str) -> bool:
        """Remove an identity from the database"""
        if identity in self.face_db:
            del self.face_db[identity]
            logger.info(f"Removed identity: {identity}")
            return True
        return False
    
    def get_all_identities(self) -> List[str]:
        """Get all enrolled identities"""
        return list(self.face_db.keys())
