"""
Unified Attendance System - Fixed Version with Better Database Handling
Single Person or Multi-Person Mode with proper error handling
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
import sqlite3
from collections import defaultdict

# Add current directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class AttendanceDatabase:
    """Database for storing attendance records with proper schema handling"""
    
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables with complete schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create attendance table with all required columns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    confidence REAL NOT NULL,
                    photo_path TEXT,
                    status TEXT DEFAULT 'present',
                    face_position TEXT DEFAULT 'unknown',
                    detection_mode TEXT DEFAULT 'single'
                )
            ''')
            
            # Create persons table with all required columns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    enrolled_date DATETIME NOT NULL,
                    photo_count INTEGER DEFAULT 0,
                    last_seen DATETIME,
                    total_attendance INTEGER DEFAULT 0
                )
            ''')
            
            # Check if we need to add missing columns to existing tables
            self.migrate_schema(cursor)
            
            conn.commit()
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def migrate_schema(self, cursor):
        """Migrate existing database schema to include new columns"""
        try:
            # Check attendance table columns
            cursor.execute("PRAGMA table_info(attendance)")
            attendance_columns = [column[1] for column in cursor.fetchall()]
            
            if 'face_position' not in attendance_columns:
                cursor.execute('ALTER TABLE attendance ADD COLUMN face_position TEXT DEFAULT "unknown"')
                print("✅ Added face_position column to attendance table")
            
            if 'detection_mode' not in attendance_columns:
                cursor.execute('ALTER TABLE attendance ADD COLUMN detection_mode TEXT DEFAULT "single"')
                print("✅ Added detection_mode column to attendance table")
            
            # Check persons table columns
            cursor.execute("PRAGMA table_info(persons)")
            person_columns = [column[1] for column in cursor.fetchall()]
            
            if 'total_attendance' not in person_columns:
                cursor.execute('ALTER TABLE persons ADD COLUMN total_attendance INTEGER DEFAULT 0')
                print("✅ Added total_attendance column to persons table")
                
                # Update existing total_attendance counts
                cursor.execute('''
                    UPDATE persons 
                    SET total_attendance = (
                        SELECT COUNT(*) 
                        FROM attendance 
                        WHERE attendance.person_name = persons.name
                    )
                ''')
        
        except Exception as e:
            print(f"Warning: Schema migration issue: {e}")
    
    def add_person(self, name: str, photo_count: int = 0):
        """Add a new person to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO persons (name, enrolled_date, photo_count, total_attendance)
                VALUES (?, ?, ?, 0)
            ''', (name, datetime.now(), photo_count))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding person: {e}")
            return False
        finally:
            conn.close()
    
    def mark_attendance(self, person_name: str, confidence: float, photo_path: str = None, face_position: str = "unknown", detection_mode: str = "single"):
        """Mark attendance for a person"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if already marked today
            today = datetime.now().date()
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE person_name = ? AND DATE(timestamp) = ?
            ''', (person_name, today))
            
            if cursor.fetchone():
                return False, "Already marked today"
            
            # Mark attendance
            cursor.execute('''
                INSERT INTO attendance (person_name, timestamp, confidence, photo_path, face_position, detection_mode)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (person_name, datetime.now(), confidence, photo_path, face_position, detection_mode))
            
            # Update last seen and increment total attendance
            cursor.execute('''
                UPDATE persons 
                SET last_seen = ?, total_attendance = total_attendance + 1 
                WHERE name = ?
            ''', (datetime.now(), person_name))
            
            conn.commit()
            return True, "Attendance marked"
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            conn.close()
    
    def get_today_attendance(self):
        """Get today's attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            cursor.execute('''
                SELECT person_name, timestamp, confidence, 
                COALESCE(face_position, 'unknown') as face_position,
                COALESCE(detection_mode, 'single') as detection_mode
                FROM attendance 
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp DESC
            ''', (today,))
            
            records = cursor.fetchall()
            return records
        except Exception as e:
            print(f"Error getting today's attendance: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_enrolled_persons(self):
        """Get all enrolled persons"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT name, COALESCE(total_attendance, 0) as total_attendance, last_seen 
                FROM persons 
                ORDER BY name
            ''')
            
            records = cursor.fetchall()
            return records
        except Exception as e:
            print(f"Error getting enrolled persons: {e}")
            return []
        finally:
            conn.close()
    
    def get_person_stats(self, person_name: str):
        """Get attendance statistics for a person"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COUNT(*) as total_days,
                       MAX(timestamp) as last_attendance,
                       AVG(confidence) as avg_confidence
                FROM attendance WHERE person_name = ?
            ''', (person_name,))
            
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error getting person stats: {e}")
            return (0, None, 0.0)
        finally:
            conn.close()

class UnifiedFaceRecognizer:
    """Unified face recognition system supporting both single and multi-person modes"""
    
    def __init__(self, multi_person_mode: bool = False):
        self.face_cascade = None
        self.enrolled_persons = {}
        self.recognition_threshold = 0.55  # Lowered for better sensitivity
        self.multi_person_mode = multi_person_mode
        
        if multi_person_mode:
            self.person_cooldowns = defaultdict(float)  # Individual cooldowns per person
            self.cooldown_duration = 5.0  # 5 seconds per person
        else:
            self.last_recognition_time = 0
            self.recognition_cooldown = 3.0  # Global cooldown for single person mode
        
    def initialize_detector(self):
        """Initialize face detector"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            return not self.face_cascade.empty()
        except Exception as e:
            print(f"Error initializing detector: {e}")
            return False
    
    def load_enrolled_persons(self):
        """Load enrolled persons from test_photos directory"""
        test_photos_dir = Path(__file__).parent / "test_photos"
        
        if not test_photos_dir.exists():
            print(f"❌ No enrollment directory found: {test_photos_dir}")
            return False
        
        self.enrolled_persons = {}
        
        for person_dir in test_photos_dir.iterdir():
            if person_dir.is_dir():
                person_name = person_dir.name
                photos = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.png"))
                
                if photos:
                    print(f"📋 Loading {person_name}: {len(photos)} photos")
                    
                    # Load and process each photo
                    face_encodings = []
                    for photo_path in photos:
                        encoding = self.extract_face_encoding(photo_path)
                        if encoding is not None:
                            face_encodings.append(encoding)
                    
                    if face_encodings:
                        self.enrolled_persons[person_name] = {
                            'encodings': face_encodings,
                            'photo_count': len(photos),
                            'valid_encodings': len(face_encodings)
                        }
                        print(f"   ✅ {person_name}: {len(face_encodings)} valid encodings")
                    else:
                        print(f"   ❌ {person_name}: No valid face encodings")
        
        print(f"\n📊 Enrollment Summary: {len(self.enrolled_persons)} persons loaded")
        return len(self.enrolled_persons) > 0
    
    def extract_face_encoding(self, photo_path: Path) -> Optional[np.ndarray]:
        """Extract face encoding from a photo"""
        try:
            image = cv2.imread(str(photo_path))
            if image is None:
                return None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhanced detection with multiple parameters
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05, 
                minNeighbors=3, 
                minSize=(40, 40)
            )
            
            if len(faces) == 0:
                # Try with more sensitive settings
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=2, 
                    minSize=(30, 30)
                )
            
            if len(faces) == 0:
                return None
            
            # Get the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Extract face region and create encoding
            face_region = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_region, (64, 64))
            
            # Normalize and flatten as encoding
            face_normalized = face_resized.astype(np.float32) / 255.0
            encoding = face_normalized.flatten()
            
            return encoding
            
        except Exception as e:
            print(f"Error extracting encoding from {photo_path}: {e}")
            return None
    
    def detect_all_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect all faces in the frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Enhanced preprocessing
            gray = cv2.equalizeHist(gray)  # Improve contrast
            
            if self.multi_person_mode:
                # Multiple detection passes for better coverage in multi-person mode
                all_faces = []
                
                # Pass 1: Standard detection
                faces1 = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(40, 40),
                    maxSize=(300, 300)
                )
                all_faces.extend(faces1)
                
                # Pass 2: More sensitive detection
                faces2 = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=2,
                    minSize=(30, 30),
                    maxSize=(400, 400)
                )
                all_faces.extend(faces2)
                
                # Remove duplicates
                unique_faces = self.remove_duplicate_faces(all_faces)
                return unique_faces
            else:
                # Single person mode - return one face
                faces = self.face_cascade.detectMultiScale(
                    gray, 1.1, 5, minSize=(50, 50)
                )
                return list(faces)
            
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def remove_duplicate_faces(self, faces: List[Tuple]) -> List[Tuple]:
        """Remove overlapping face detections (for multi-person mode)"""
        if len(faces) <= 1:
            return faces
        
        faces = list(faces)
        unique_faces = []
        
        for face in faces:
            x, y, w, h = face
            is_duplicate = False
            
            for existing in unique_faces:
                ex, ey, ew, eh = existing
                
                # Calculate overlap
                overlap_x = max(0, min(x + w, ex + ew) - max(x, ex))
                overlap_y = max(0, min(y + h, ey + eh) - max(y, ey))
                overlap_area = overlap_x * overlap_y
                
                face_area = w * h
                existing_area = ew * eh
                
                # If overlap is significant, consider it duplicate
                if overlap_area > 0.4 * min(face_area, existing_area):
                    is_duplicate = True
                    # Keep the larger face
                    if face_area > existing_area:
                        unique_faces.remove(existing)
                        unique_faces.append(face)
                    break
            
            if not is_duplicate:
                unique_faces.append(face)
        
        return unique_faces
    
    def recognize_face_single(self, frame: np.ndarray) -> Tuple[Optional[str], float, Tuple[int, int, int, int]]:
        """Recognize single face (single person mode)"""
        try:
            faces = self.detect_all_faces(frame)
            
            if len(faces) == 0:
                return None, 0.0, (0, 0, 0, 0)
            
            # Get the largest face
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = face
            
            # Extract face encoding
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_region = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_region, (64, 64))
            face_normalized = face_resized.astype(np.float32) / 255.0
            current_encoding = face_normalized.flatten()
            
            # Compare with enrolled persons
            best_match = None
            best_similarity = 0.0
            
            for person_name, person_data in self.enrolled_persons.items():
                for enrolled_encoding in person_data['encodings']:
                    # Calculate similarity (correlation coefficient)
                    similarity = np.corrcoef(current_encoding, enrolled_encoding)[0, 1]
                    if np.isnan(similarity):
                        similarity = 0.0
                    
                    similarity = max(0, similarity)  # Ensure positive
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = person_name
            
            # Return result if above threshold
            if best_similarity >= self.recognition_threshold:
                return best_match, best_similarity, (x, y, w, h)
            else:
                return "Unknown", best_similarity, (x, y, w, h)
                
        except Exception as e:
            print(f"Single recognition error: {e}")
            return None, 0.0, (0, 0, 0, 0)
    
    def recognize_all_faces(self, frame: np.ndarray) -> List[Dict]:
        """Recognize all faces (multi-person mode)"""
        faces = self.detect_all_faces(frame)
        recognition_results = []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for i, (x, y, w, h) in enumerate(faces):
            try:
                # Extract face encoding
                face_region = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_region, (64, 64))
                face_normalized = face_resized.astype(np.float32) / 255.0
                current_encoding = face_normalized.flatten()
                
                # Compare with enrolled persons
                best_match = None
                best_similarity = 0.0
                
                for person_name, person_data in self.enrolled_persons.items():
                    max_similarity_for_person = 0.0
                    
                    for enrolled_encoding in person_data['encodings']:
                        # Enhanced similarity calculation
                        try:
                            # Correlation coefficient
                            corr = np.corrcoef(current_encoding, enrolled_encoding)[0, 1]
                            if np.isnan(corr):
                                corr = 0.0
                            corr = max(0, corr)
                            
                            # Cosine similarity
                            dot_product = np.dot(current_encoding, enrolled_encoding)
                            norm_current = np.linalg.norm(current_encoding)
                            norm_enrolled = np.linalg.norm(enrolled_encoding)
                            cosine_sim = dot_product / (norm_current * norm_enrolled)
                            cosine_sim = max(0, cosine_sim)
                            
                            # Combined similarity
                            similarity = (0.7 * corr + 0.3 * cosine_sim)
                            
                            if similarity > max_similarity_for_person:
                                max_similarity_for_person = similarity
                        except:
                            continue
                    
                    if max_similarity_for_person > best_similarity:
                        best_similarity = max_similarity_for_person
                        best_match = person_name
                
                # Determine recognition result
                if best_similarity >= self.recognition_threshold:
                    recognized_name = best_match
                    status = "recognized"
                else:
                    recognized_name = "Unknown"
                    status = "unknown"
                
                # Check cooldown for this specific person
                current_time = time.time()
                can_mark_attendance = True
                
                if recognized_name in self.person_cooldowns:
                    time_since_last = current_time - self.person_cooldowns[recognized_name]
                    can_mark_attendance = time_since_last >= self.cooldown_duration
                
                recognition_results.append({
                    'face_id': i,
                    'person_name': recognized_name,
                    'confidence': best_similarity,
                    'face_box': (x, y, w, h),
                    'status': status,
                    'can_mark_attendance': can_mark_attendance,
                    'face_position': f"({x},{y},{w},{h})"
                })
                
            except Exception as e:
                print(f"Error recognizing face {i}: {e}")
                recognition_results.append({
                    'face_id': i,
                    'person_name': "Error",
                    'confidence': 0.0,
                    'face_box': (x, y, w, h),
                    'status': "error",
                    'can_mark_attendance': False,
                    'face_position': f"({x},{y},{w},{h})"
                })
        
        return recognition_results
    
    def update_person_cooldown(self, person_name: str):
        """Update cooldown for a specific person (multi-person mode)"""
        if self.multi_person_mode:
            self.person_cooldowns[person_name] = time.time()
    
    def check_global_cooldown(self) -> bool:
        """Check global cooldown (single person mode)"""
        if not self.multi_person_mode:
            current_time = time.time()
            return current_time - self.last_recognition_time > self.recognition_cooldown
        return True
    
    def update_global_cooldown(self):
        """Update global cooldown (single person mode)"""
        if not self.multi_person_mode:
            self.last_recognition_time = time.time()

class UnifiedAttendanceSystem:
    """Main unified attendance system supporting both single and multi-person modes"""
    
    def __init__(self, multi_person_mode: bool = False):
        self.multi_person_mode = multi_person_mode
        self.camera = None
        self.recognizer = UnifiedFaceRecognizer(multi_person_mode)
        self.database = AttendanceDatabase()
        self.is_running = False
        self.attendance_log = []
        self.frame_count = 0
        
        # Mode-specific settings
        if multi_person_mode:
            self.system_name = "MULTI-PERSON ATTENDANCE SYSTEM"
            self.detection_mode = "multi"
        else:
            self.system_name = "SINGLE PERSON ATTENDANCE SYSTEM"
            self.detection_mode = "single"
        
    def initialize_system(self):
        """Initialize the complete system"""
        print(f"🚀 Initializing {self.system_name}...")
        
        # Initialize face detector
        if not self.recognizer.initialize_detector():
            print("❌ Failed to initialize face detector")
            return False
        print("✅ Face detector initialized")
        
        # Load enrolled persons
        if not self.recognizer.load_enrolled_persons():
            print("❌ No enrolled persons found")
            print("💡 Run 'python organize_photos.py' to enroll persons first")
            return False
        
        # Add enrolled persons to database
        for person_name, data in self.recognizer.enrolled_persons.items():
            self.database.add_person(person_name, data['photo_count'])
        
        # Initialize camera
        if not self.initialize_camera():
            print("❌ Failed to initialize camera")
            return False
        
        print(f"✅ {self.system_name} initialization complete!")
        return True
    
    def initialize_camera(self, camera_index=0):
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ Camera initialized")
            return True
            
        except Exception as e:
            print(f"Camera error: {e}")
            return False
    
    def draw_interface(self, frame: np.ndarray) -> np.ndarray:
        """Draw the attendance interface on frame"""
        height, width = frame.shape[:2]
        
        # Draw title
        title = self.system_name
        cv2.putText(frame, title, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw mode indicator
        mode_text = f"Mode: {'Multi-Person' if self.multi_person_mode else 'Single Person'}"
        cv2.putText(frame, mode_text, (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, height - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Draw enrolled persons count
        enrolled_count = len(self.recognizer.enrolled_persons)
        cv2.putText(frame, f'Enrolled: {enrolled_count} persons', (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw today's attendance count
        today_attendance = self.database.get_today_attendance()
        cv2.putText(frame, f'Today: {len(today_attendance)} present', (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw frame count
        cv2.putText(frame, f'Frame: {self.frame_count}', (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        return frame
    
    def draw_single_recognition_result(self, frame: np.ndarray, person_name: str, 
                                     confidence: float, face_box: Tuple[int, int, int, int]) -> np.ndarray:
        """Draw recognition result for single person mode"""
        if face_box[2] == 0 and face_box[3] == 0:  # No face detected
            return frame
        
        x, y, w, h = face_box
        
        # Draw face rectangle
        if person_name == "Unknown":
            color = (0, 0, 255)  # Red for unknown
            status = "UNKNOWN PERSON"
        elif person_name is None:
            color = (255, 255, 0)  # Yellow for detection
            status = "DETECTING..."
        else:
            color = (0, 255, 0)  # Green for recognized
            status = f"RECOGNIZED: {person_name}"
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # Draw person name and confidence
        if person_name:
            text_y = y - 10 if y > 30 else y + h + 20
            cv2.putText(frame, status, (x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            if confidence > 0:
                conf_text = f'Confidence: {confidence:.1%}'
                cv2.putText(frame, conf_text, (x, text_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame
    
    def draw_multi_recognition_results(self, frame: np.ndarray, recognition_results: List[Dict]) -> np.ndarray:
        """Draw recognition results for multi-person mode"""
        for result in recognition_results:
            x, y, w, h = result['face_box']
            person_name = result['person_name']
            confidence = result['confidence']
            status = result['status']
            can_mark = result['can_mark_attendance']
            
            # Choose color based on status
            if status == "recognized":
                if can_mark:
                    color = (0, 255, 0)  # Green - can mark attendance
                    status_text = f"READY: {person_name}"
                else:
                    color = (0, 255, 255)  # Yellow - already marked
                    status_text = f"DONE: {person_name}"
            elif status == "unknown":
                color = (0, 0, 255)  # Red - unknown person
                status_text = "UNKNOWN PERSON"
            else:
                color = (128, 128, 128)  # Gray - error
                status_text = "ERROR"
            
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw person name and confidence
            text_y = y - 10 if y > 30 else y + h + 20
            cv2.putText(frame, status_text, (x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 2)
            
            if confidence > 0:
                conf_text = f'Conf: {confidence:.1%}'
                cv2.putText(frame, conf_text, (x, text_y + 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
            
            # Draw face ID
            cv2.putText(frame, f'ID:{result["face_id"]}', (x + w - 30, y + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Draw summary at top right
        detected_count = len(recognition_results)
        recognized_count = sum(1 for r in recognition_results if r['status'] == 'recognized')
        ready_count = sum(1 for r in recognition_results if r['can_mark_attendance'] and r['status'] == 'recognized')
        
        summary_x = frame.shape[1] - 200
        cv2.putText(frame, f'Faces: {detected_count}', (summary_x, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f'Recognized: {recognized_count}', (summary_x, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(frame, f'Ready: {ready_count}', (summary_x, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        return frame
    
    def save_attendance_photo(self, frame: np.ndarray, person_name: str) -> str:
        """Save photo when attendance is marked"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create attendance photos directory
        photos_dir = Path(__file__).parent / "attendance_photos"
        photos_dir.mkdir(exist_ok=True)
        
        # Save photo with mode indicator
        mode_prefix = "multi" if self.multi_person_mode else "single"
        photo_path = photos_dir / f"{mode_prefix}_{person_name}_{timestamp}.jpg"
        cv2.imwrite(str(photo_path), frame)
        
        return str(photo_path)
    
    def run_attendance_system(self):
        """Run the unified attendance system"""
        if not self.initialize_system():
            return False
        
        print(f"\n🎥 {self.system_name} STARTED")
        print("=" * 70)
        print("📋 Enrolled Persons:")
        for person_name, data in self.recognizer.enrolled_persons.items():
            print(f"   - {person_name} ({data['valid_encodings']} photos)")
        
        print(f"\n🚀 Starting camera feed...")
        if self.multi_person_mode:
            print("💡 Multiple people can be detected and marked simultaneously")
            print("💡 Each person has individual 5-second cooldown")
        else:
            print("💡 Position yourself in front of the camera for attendance")
            print("💡 Global 3-second cooldown between recognitions")
        
        self.is_running = True
        
        try:
            while self.is_running:
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to read from camera")
                    break
                
                self.frame_count += 1
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Draw interface
                frame = self.draw_interface(frame)
                
                # Perform recognition based on mode
                recognition_interval = 3 if self.multi_person_mode else 5
                
                if self.frame_count % recognition_interval == 0:
                    if self.multi_person_mode:
                        # Multi-person mode
                        recognition_results = self.recognizer.recognize_all_faces(frame)
                        frame = self.draw_multi_recognition_results(frame, recognition_results)
                        
                        # Process attendance for each recognized person
                        for result in recognition_results:
                            if (result['status'] == 'recognized' and 
                                result['can_mark_attendance'] and 
                                result['person_name'] != 'Unknown'):
                                
                                person_name = result['person_name']
                                confidence = result['confidence']
                                face_position = result['face_position']
                                
                                # Save photo and mark attendance
                                photo_path = self.save_attendance_photo(frame, person_name)
                                success, message = self.database.mark_attendance(
                                    person_name, confidence, photo_path, face_position, self.detection_mode
                                )
                                
                                if success:
                                    print(f"\n✅ ATTENDANCE MARKED: {person_name} ({confidence:.1%}) - Face ID: {result['face_id']}")
                                    self.attendance_log.append({
                                        'person': person_name,
                                        'time': datetime.now(),
                                        'confidence': confidence,
                                        'face_id': result['face_id'],
                                        'mode': 'multi'
                                    })
                                    
                                    # Update cooldown for this person
                                    self.recognizer.update_person_cooldown(person_name)
                                else:
                                    print(f"\n⚠️  {person_name}: {message}")
                    
                    else:
                        # Single person mode
                        person_name, confidence, face_box = self.recognizer.recognize_face_single(frame)
                        frame = self.draw_single_recognition_result(frame, person_name, confidence, face_box)
                        
                        # Mark attendance if person recognized and cooldown passed
                        if (person_name and person_name != "Unknown" and 
                            self.recognizer.check_global_cooldown()):
                            
                            # Save photo and mark attendance
                            photo_path = self.save_attendance_photo(frame, person_name)
                            face_position = f"({face_box[0]},{face_box[1]},{face_box[2]},{face_box[3]})"
                            success, message = self.database.mark_attendance(
                                person_name, confidence, photo_path, face_position, self.detection_mode
                            )
                            
                            if success:
                                print(f"\n✅ ATTENDANCE MARKED: {person_name} ({confidence:.1%})")
                                self.attendance_log.append({
                                    'person': person_name,
                                    'time': datetime.now(),
                                    'confidence': confidence,
                                    'mode': 'single'
                                })
                            else:
                                print(f"\n⚠️  {person_name}: {message}")
                            
                            self.recognizer.update_global_cooldown()
                
                # Save frame periodically (headless mode)
                if self.frame_count % 60 == 0:  # Save every 2 seconds
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    frame_dir = Path(__file__).parent / "live_frames"
                    frame_dir.mkdir(exist_ok=True)
                    mode_prefix = "multi" if self.multi_person_mode else "single"
                    frame_path = frame_dir / f"{mode_prefix}_attendance_{timestamp}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                
                # Check for quit (simulated with time limit for headless mode)
                time.sleep(0.05)  # 20 FPS for better responsiveness
                
                # Auto-quit after 10 minutes for demo
                if self.frame_count > 12000:  # 10 minutes at 20 FPS
                    print("\n⏰ Demo time limit reached")
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ System stopped by user")
        
        finally:
            self.cleanup()
            self.print_session_summary()
    
    def print_session_summary(self):
        """Print attendance session summary"""
        print(f"\n📊 {self.system_name} SESSION SUMMARY")
        print("=" * 60)
        
        today_attendance = self.database.get_today_attendance()
        print(f"Total attendance today: {len(today_attendance)}")
        
        if today_attendance:
            print(f"\n📋 Today's Attendance:")
            for person_name, timestamp, confidence, face_position, detection_mode in today_attendance:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                mode_indicator = f"[{detection_mode.upper()}]"
                if face_position and face_position != "unknown":
                    print(f"   ✅ {person_name} - {time_str} ({confidence:.1%}) {mode_indicator} - Pos: {face_position}")
                else:
                    print(f"   ✅ {person_name} - {time_str} ({confidence:.1%}) {mode_indicator}")
        
        # Show all enrolled persons status
        print(f"\n👥 All Enrolled Persons Status:")
        all_persons = self.database.get_all_enrolled_persons()
        for name, total_attendance, last_seen in all_persons:
            if last_seen:
                last_seen_str = datetime.fromisoformat(last_seen).strftime("%Y-%m-%d %H:%M")
                status = "✅ Present today" if any(p[0] == name for p in today_attendance) else "❌ Absent today"
            else:
                last_seen_str = "Never"
                status = "❌ Never attended"
            
            print(f"   👤 {name}: {total_attendance} total days, last: {last_seen_str} - {status}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.camera:
            self.camera.release()
        print(f"🧹 {self.system_name} cleanup completed")

def select_mode():
    """Select attendance system mode"""
    print("💡 Choose attendance detection mode:")
    print()
    print("1. Single Person Mode")
    print("   - Detects one person at a time")
    print("   - Global 3-second cooldown")
    print("   - Simpler processing")
    print()
    print("2. Multi-Person Mode")
    print("   - Detects multiple people simultaneously")
    print("   - Individual 5-second cooldowns per person")
    print("   - Advanced processing")
    print()
    
    while True:
        try:
            choice = input("Enter choice (1 for Single, 2 for Multi, or press Enter for Single): ").strip()
            
            if choice == "" or choice == "1":
                return False  # Single person mode
            elif choice == "2":
                return True   # Multi-person mode
            else:
                print("⚠️ Invalid choice. Please enter 1 or 2.")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return None

def check_and_fix_database():
    """Check database and fix if needed"""
    db_path = "attendance.db"
    
    if Path(db_path).exists():
        print("📁 Found existing database, checking schema...")
        
        # Try to create a test connection and check schema
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if required columns exist
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [column[1] for column in cursor.fetchall()]
            
            missing_columns = []
            required_columns = ['face_position', 'detection_mode']
            
            for col in required_columns:
                if col not in columns:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"⚠️ Missing columns detected: {missing_columns}")
                print("🔧 The database will be automatically updated...")
            else:
                print("✅ Database schema is up to date")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Database check error: {e}")
            print("🔧 Database will be recreated...")
    else:
        print("📁 No existing database found, will create new one")

def main():
    """Main function with better error handling"""
    print("🎭 TRUE PRESENCE - UNIFIED ATTENDANCE SYSTEM (FIXED)")
    print("=" * 70)
    
    # Check and fix database first
    check_and_fix_database()
    
    # Check if persons are enrolled
    test_photos_dir = Path(__file__).parent / "test_photos"
    if not test_photos_dir.exists() or not any(test_photos_dir.iterdir()):
        print("\n❌ No enrolled persons found!")
        print("📋 Please enroll persons first:")
        print("   1. python headless_camera_test.py  # Capture photos")
        print("   2. python organize_photos.py       # Organize for enrollment")
        print("   3. python simple_opencv_test.py    # Test recognition")
        print("   4. python unified_attendance_system_fixed.py # Start attendance")
        return False
    
    # Select mode
    multi_person_mode = select_mode()
    if multi_person_mode is None:
        return False
    
    # Initialize and run system
    try:
        system = UnifiedAttendanceSystem(multi_person_mode)
        success = system.run_attendance_system()
        return success
    except Exception as e:
        print(f"❌ System error: {e}")
        print("💡 Try running the database fix script:")
        print("   python fix_database.py")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)