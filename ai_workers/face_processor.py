# import cv2
# import numpy as np
# from mtcnn import MTCNN
# from deepface import DeepFace
# # Note: You will need to find and integrate a separate anti-spoofing model.
# # For this example, we will simulate it with a placeholder function.

# class FaceProcessor:
#     """
#     A class to handle face detection, anti-spoofing, and recognition.
#     This class is designed to be initialized once to load all models into memory.
#     """
#     def __init__(self):
#         """
#         Initializes the models. This can be time-consuming and should only be
#         done once when the worker starts.
#         """
#         print("Loading AI models, this may take a moment...")
#         self.detector = MTCNN()
#         # The 'represent' function in DeepFace handles loading the ArcFace model.
#         # We do a dummy call to ensure the model is loaded into memory on init.
#         print("Warming up ArcFace model...")
#         dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
#         DeepFace.represent(dummy_image, model_name='ArcFace', enforce_detection=False)
        
#         # In a real application, you would load your trained anti-spoofing model here.
#         # self.liveness_model = load_liveness_model('path/to/your/liveness_model.h5')
#         print("FaceProcessor initialized successfully.")

#     def _is_live(self, face_crop: np.ndarray) -> bool:
#         """
#         Placeholder for the anti-spoofing model.
#         In a real system, this would feed the face_crop into a liveness detection CNN.
        
#         Args:
#             face_crop (np.ndarray): The cropped image of the face.

#         Returns:
#             bool: True if the face is determined to be live, False otherwise.
#         """
#         # --- Placeholder Logic ---
#         # Replace this with your actual model prediction.
#         # For example: prediction = self.liveness_model.predict(face_crop)
#         # return prediction[0][1] > 0.95 # e.g., if real_prob > 95%
#         return True # Simulating a "REAL" face for now.

#     def process_frame(self, frame: np.ndarray) -> list:
#         """
#         Processes a single video frame to find and analyze all faces.

#         Args:
#             frame (np.ndarray): The input image frame from the camera.

#         Returns:
#             list: A list of dictionaries, where each dictionary contains
#                   information about a detected face (bbox, liveness, embedding).
#         """
#         results = []
        
#         # 1. Face Detection using MTCNN
#         detected_faces = self.detector.detect_faces(frame)

#         if not detected_faces:
#             return []

#         for face_data in detected_faces:
#             x, y, w, h = face_data['box']
#             # Ensure coordinates are within image bounds and positive
#             x, y = max(0, x), max(0, y)
            
#             face_info = {
#                 "bbox": [x, y, w, h],
#                 "is_live": False,
#                 "embedding": None
#             }

#             # 2. Anti-Spoofing (Liveness Detection)
#             face_crop = frame[y:y+h, x:x+w]
            
#             # Check if crop is valid before processing
#             if face_crop.size == 0:
#                 continue

#             if self._is_live(face_crop):
#                 face_info["is_live"] = True
                
#                 try:
#                     # 3. Face Recognition (Embedding Generation) using ArcFace
#                     # We pass the cropped face directly for representation
#                     embedding = DeepFace.represent(
#                         img_path=face_crop,
#                         model_name='ArcFace',
#                         enforce_detection=False, # We already detected the face
#                         detector_backend='skip'
#                     )
#                     if embedding and len(embedding) > 0:
#                          face_info["embedding"] = embedding[0]["embedding"]

#                 except Exception as e:
#                     print(f"Could not generate embedding for a face: {e}")
#                     # Face might be too blurry, occluded, or at a sharp angle
#                     pass

#             results.append(face_info)
            
#         return results

# # --- Example Usage (for testing this module directly) ---
# if __name__ == '__main__':
#     # This block will only run when you execute `python face_processor.py`
    
#     # Initialize the processor (loads models)
#     processor = FaceProcessor()

#     # Load a test image
#     # Make sure you have a file named 'test_image.jpg' in the same directory
#     try:
#         test_frame = cv2.imread("test_image.jpg")
#         if test_frame is None:
#             raise FileNotFoundError("test_image.jpg not found or could not be read.")
        
#         # Process the frame
#         processed_results = processor.process_frame(test_frame)

#         # Print and display the results
#         print(f"\nFound {len(processed_results)} faces.")
#         for i, result in enumerate(processed_results):
#             print(f"\n--- Face {i+1} ---")
#             print(f"  Bounding Box: {result['bbox']}")
#             print(f"  Is Live: {result['is_live']}")
            
#             if result['embedding']:
#                 print(f"  Embedding Vector (first 5 values): {result['embedding'][:5]}...")
#                 print(f"  Embedding Vector Length: {len(result['embedding'])}")
#             else:
#                 print("  Embedding: Not generated (face might be fake or low quality).")

#             # Draw on the image for visualization
#             x, y, w, h = result['bbox']
#             color = (0, 255, 0) if result['is_live'] else (0, 0, 255)
#             label = "LIVE" if result['is_live'] else "SPOOF"
#             cv2.rectangle(test_frame, (x, y), (x+w, y+h), color, 2)
#             cv2.putText(test_frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
#         cv2.imwrite("output_image.jpg", test_frame)
#         print("\nOutput image with detections saved as 'output_image.jpg'")

#     except FileNotFoundError as e:
#         print(e)
#     except Exception as e:
#         print(f"An error occurred during testing: {e}")
import cv2
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace

class FaceProcessor:
    """
    A class to handle face detection, anti-spoofing, and recognition.
    Uses MTCNN for detection, DeepFace ArcFace for embeddings, and placeholder for anti-spoofing.
    """
    def __init__(self):
        """
        Initializes the models. This can be time-consuming and should only be
        done once when the worker starts.
        """
        print("Loading AI models, this may take a moment...")
        
        # 1. Initialize MTCNN for face detection
        self.detector = MTCNN()
        
        # 2. Warm up DeepFace ArcFace model
        print("Warming up DeepFace ArcFace model...")
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        try:
            DeepFace.represent(dummy_image, model_name='ArcFace', enforce_detection=False)
            print("DeepFace ArcFace model warmed up successfully.")
        except Exception as e:
            print(f"Error warming up DeepFace: {e}")
        
        # 3. Placeholder for anti-spoofing model
        # In a real application, you would load your trained liveness detection model here
        # self.liveness_model = load_model('path/to/liveness_model.h5')
        
        print("FaceProcessor initialized successfully.")

    def _is_live(self, face_crop: np.ndarray) -> bool:
        """
        Placeholder for the anti-spoofing/liveness detection model.
        In a real system, this would feed the face_crop into a CNN for liveness detection.
        
        Args:
            face_crop (np.ndarray): The cropped image of the face.

        Returns:
            bool: True if the face is determined to be live, False otherwise.
        """
        # For now, perform basic checks
        if face_crop.size == 0:
            return False
        
        # Simple heuristic: check if face has enough variance (not a flat image)
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        
        # Very simple check - in reality you'd use a proper CNN model
        return variance > 100  # Threshold for image variance

    def get_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Get face embedding using DeepFace ArcFace model.
        
        Args:
            face_crop (np.ndarray): Cropped face image
            
        Returns:
            np.ndarray: Face embedding vector or None if failed
        """
        try:
            embedding_result = DeepFace.represent(
                img_path=face_crop,
                model_name='ArcFace',
                enforce_detection=False,
                detector_backend='skip'
            )
            if embedding_result and len(embedding_result) > 0:
                return np.array(embedding_result[0]["embedding"])
        except Exception as e:
            print(f"DeepFace embedding extraction failed: {e}")
        
        return None

    def process_frame(self, frame: np.ndarray) -> list:
        """
        Processes a single video frame to find and analyze all faces.

        Args:
            frame (np.ndarray): The input image frame from the camera.

        Returns:
            list: A list of dictionaries, where each dictionary contains
                  information about a detected face (bbox, liveness, embedding).
        """
        results = []
        
        # 1. Face Detection using MTCNN
        detected_faces = self.detector.detect_faces(frame)

        if not detected_faces:
            return []

        for face_data in detected_faces:
            x, y, w, h = face_data['box']
            # Ensure coordinates are within image bounds and positive
            x, y = max(0, x), max(0, y)
            w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)
            
            face_info = {
                "bbox": [x, y, w, h],
                "confidence": face_data.get('confidence', 0.0),
                "is_live": False,
                "embedding": None
            }

            # 2. Extract face crop
            face_crop = frame[y:y+h, x:x+w]
            
            # Check if crop is valid before processing
            if face_crop.size == 0 or face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
                continue

            # 3. Anti-Spoofing (Liveness Detection)
            if self._is_live(face_crop):
                face_info["is_live"] = True
                
                # 4. Face Recognition (Embedding Generation) using ArcFace
                embedding = self.get_embedding(face_crop)
                if embedding is not None:
                    face_info["embedding"] = embedding.tolist()

            results.append(face_info)
            
        return results

    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray, threshold: float = 0.6) -> dict:
        """
        Compare two face embeddings and return similarity score.
        
        Args:
            embedding1 (np.ndarray): First face embedding
            embedding2 (np.ndarray): Second face embedding
            threshold (float): Similarity threshold for matching
            
        Returns:
            dict: Contains similarity score and match status
        """
        if embedding1 is None or embedding2 is None:
            return {"similarity": 0.0, "is_match": False}
        
        # Convert to numpy arrays if they're lists
        if isinstance(embedding1, list):
            embedding1 = np.array(embedding1)
        if isinstance(embedding2, list):
            embedding2 = np.array(embedding2)
        
        # Calculate cosine similarity
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return {"similarity": 0.0, "is_match": False}
        
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        is_match = similarity > threshold
        
        return {
            "similarity": float(similarity),
            "is_match": bool(is_match)
        }

# --- Example Usage (for testing this module directly) ---
if __name__ == '__main__':
    # This block will only run when you execute `python face_processor.py`
    
    # Initialize the processor (loads models)
    processor = FaceProcessor()

    # Load a test image
    try:
        test_frame = cv2.imread("test_image.jpg")
        if test_frame is None:
            # Create a dummy test image if file doesn't exist
            print("test_image.jpg not found, creating dummy test image...")
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Process the frame
        processed_results = processor.process_frame(test_frame)

        # Print and display the results
        print(f"\nFound {len(processed_results)} faces.")
        for i, result in enumerate(processed_results):
            print(f"\n--- Face {i+1} ---")
            print(f"  Bounding Box: {result['bbox']}")
            print(f"  Confidence: {result['confidence']:.3f}")
            print(f"  Is Live: {result['is_live']}")
            
            if result['embedding']:
                print(f"  Embedding Vector (first 5 values): {result['embedding'][:5]}...")
                print(f"  Embedding Vector Length: {len(result['embedding'])}")
            else:
                print("  Embedding: Not generated (face might be fake or low quality).")

            # Draw on the image for visualization
            x, y, w, h = result['bbox']
            color = (0, 255, 0) if result['is_live'] else (0, 0, 255)
            label = f"LIVE ({result['confidence']:.2f})" if result['is_live'] else "SPOOF"
            cv2.rectangle(test_frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(test_frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        cv2.imwrite("output_image.jpg", test_frame)
        print("\nOutput image with detections saved as 'output_image.jpg'")

    except Exception as e:
        print(f"An error occurred during testing: {e}")