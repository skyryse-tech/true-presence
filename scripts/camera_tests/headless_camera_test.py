"""
Headless Camera Face Detection Test - Saves images instead of displaying windows
Works without GUI support - perfect for your OpenCV installation
"""

import os
import sys
import numpy as np
import cv2
from typing import Dict, Any, List, Tuple
from pathlib import Path
import time

# Add current directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class HeadlessFaceDetection:
    """Headless camera face detection class - saves images instead of showing"""
    
    def __init__(self):
        self.face_cascade = None
        self.camera = None
        self.is_running = False
        self.frame_count = 0
        
    def initialize_camera(self, camera_index=0):
        """Initialize camera"""
        print(f"🎥 Initializing camera {camera_index}...")
        
        try:
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                print(f"❌ Failed to open camera {camera_index}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Test camera
            ret, frame = self.camera.read()
            if not ret:
                print(f"❌ Failed to read from camera {camera_index}")
                return False
            
            print(f"✅ Camera initialized successfully")
            print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization error: {e}")
            return False
    
    def initialize_face_detector(self):
        """Initialize face detector"""
        print(f"🔍 Initializing face detector...")
        
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                print(f"❌ Failed to load face cascade")
                return False
            
            print(f"✅ Face detector initialized")
            return True
            
        except Exception as e:
            print(f"❌ Face detector error: {e}")
            return False
    
    def detect_faces_in_frame(self, frame):
        """Detect faces in a single frame"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return faces
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def draw_face_info(self, frame, faces):
        """Draw face detection info on frame"""
        height, width = frame.shape[:2]
        
        # Draw faces
        for i, (x, y, w, h) in enumerate(faces):
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Face number
            cv2.putText(frame, f'Face {i+1}', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Face size info
            face_area = w * h
            total_area = width * height
            percentage = (face_area / total_area) * 100
            
            size_text = f'{w}x{h} ({percentage:.1f}%)'
            cv2.putText(frame, size_text, (x, y + h + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            
            # Face quality indicators
            if percentage < 10:
                quality_text = "Too Small"
                color = (0, 0, 255)  # Red
            elif percentage > 50:
                quality_text = "Too Large"
                color = (0, 165, 255)  # Orange
            else:
                quality_text = "Good Size"
                color = (0, 255, 0)  # Green
            
            cv2.putText(frame, quality_text, (x, y + h + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame
    
    def draw_ui_info(self, frame):
        """Draw UI information on frame"""
        height, width = frame.shape[:2]
        
        # Title
        cv2.putText(frame, 'True Presence - Face Detection', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Frame count
        cv2.putText(frame, f'Frame: {self.frame_count}', (width - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def save_frame_with_detection(self, frame, faces, save_dir):
        """Save frame with detection results"""
        # Fix: Use simpler timestamp format
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        milliseconds = int((time.time() % 1) * 1000)
        full_timestamp = f"{timestamp}_{milliseconds:03d}"
        
        # Draw detection info
        annotated_frame = self.draw_face_info(frame.copy(), faces)
        annotated_frame = self.draw_ui_info(annotated_frame)
        
        # Show face count
        face_count_text = f'Faces: {len(faces)}'
        cv2.putText(annotated_frame, face_count_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Save annotated frame
        annotated_path = save_dir / f"detection_{full_timestamp}.jpg"
        cv2.imwrite(str(annotated_path), annotated_frame)
        
        # Also save original frame
        original_path = save_dir / f"original_{full_timestamp}.jpg"
        cv2.imwrite(str(original_path), frame)
        
        return annotated_path, original_path
    
    def run_headless_detection(self, duration_seconds=30, save_interval=2):
        """Run headless face detection for specified duration"""
        print(f"\n🎥 Starting headless face detection...")
        print(f"   Duration: {duration_seconds} seconds")
        print(f"   Save interval: {save_interval} seconds")
        print("=" * 50)
        
        if not self.initialize_face_detector():
            return False
        
        # Try cameras
        camera_indices = [0, 1, 2]
        camera_initialized = False
        current_camera = 0
        
        for camera_index in camera_indices:
            if self.initialize_camera(camera_index):
                camera_initialized = True
                current_camera = camera_index
                break
        
        if not camera_initialized:
            print(f"❌ No cameras found.")
            return False
        
        # Create save directory
        saves_dir = Path(__file__).parent / "headless_captures"
        saves_dir.mkdir(exist_ok=True)
        print(f"📁 Saving to: {saves_dir}")
        
        start_time = time.time()
        last_save_time = 0
        saved_count = 0
        total_faces_detected = 0
        
        print(f"\n🚀 Detection started! Running for {duration_seconds} seconds...")
        
        try:
            while time.time() - start_time < duration_seconds:
                # Read frame
                ret, frame = self.camera.read()
                if not ret:
                    print(f"❌ Failed to read frame")
                    break
                
                self.frame_count += 1
                
                # Flip frame horizontally (mirror effect)
                frame = cv2.flip(frame, 1)
                
                # Detect faces
                faces = self.detect_faces_in_frame(frame)
                
                if len(faces) > 0:
                    total_faces_detected += len(faces)
                
                # Save frame at intervals
                current_time = time.time()
                if current_time - last_save_time >= save_interval:
                    annotated_path, original_path = self.save_frame_with_detection(
                        frame, faces, saves_dir
                    )
                    saved_count += 1
                    last_save_time = current_time
                    
                    # Print progress
                    elapsed = current_time - start_time
                    remaining = duration_seconds - elapsed
                    print(f"⏱️  {elapsed:.1f}s | Saved {saved_count} | Faces: {len(faces)} | Remaining: {remaining:.1f}s")
                
                # Small delay to prevent overwhelming
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print(f"\n⚠️ Interrupted by user")
        
        finally:
            # Cleanup
            if self.camera:
                self.camera.release()
            
            # Final statistics
            total_time = time.time() - start_time
            print(f"\n📊 DETECTION SUMMARY")
            print("=" * 30)
            print(f"Total time: {total_time:.1f} seconds")
            print(f"Frames processed: {self.frame_count}")
            print(f"Images saved: {saved_count}")
            print(f"Total faces detected: {total_faces_detected}")
            print(f"Average faces per frame: {total_faces_detected/max(self.frame_count,1):.2f}")
            print(f"Saved to: {saves_dir}")
            
            return True

def quick_camera_test():
    """Quick test to capture a few photos"""
    print("📸 Quick Camera Test - Capture 5 photos")
    print("=" * 40)
    
    detector = HeadlessFaceDetection()
    
    if not detector.initialize_face_detector():
        return False
    
    if not detector.initialize_camera(0):
        return False
    
    # Create save directory
    saves_dir = Path(__file__).parent / "quick_test_photos"
    saves_dir.mkdir(exist_ok=True)
    
    print(f"📁 Saving photos to: {saves_dir}")
    print(f"📷 Taking 5 photos with 2-second intervals...")
    
    for i in range(5):
        print(f"\n📸 Taking photo {i+1}/5...")
        
        try:
            # Read frame
            ret, frame = detector.camera.read()
            if not ret:
                print(f"❌ Failed to capture photo {i+1}")
                continue
            
            # Flip frame
            frame = cv2.flip(frame, 1)
            
            # Detect faces
            faces = detector.detect_faces_in_frame(frame)
            
            # Save with timestamp (fixed format)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            photo_number = f"{timestamp}_{i+1:02d}"
            
            annotated_path, original_path = detector.save_frame_with_detection(
                frame, faces, saves_dir
            )
            
            print(f"   ✅ Saved: {annotated_path.name}")
            print(f"   👥 Faces detected: {len(faces)}")
            
            # Show face details if detected
            if len(faces) > 0:
                for j, (x, y, w, h) in enumerate(faces):
                    face_area = w * h
                    total_area = frame.shape[0] * frame.shape[1]
                    percentage = (face_area / total_area) * 100
                    print(f"      Face {j+1}: {w}x{h} ({percentage:.1f}% of image)")
            else:
                print(f"      💡 Try positioning yourself in front of the camera")
            
            if i < 4:  # Don't wait after last photo
                print(f"   ⏳ Waiting 2 seconds...")
                time.sleep(2)
                
        except Exception as e:
            print(f"   ❌ Error capturing photo {i+1}: {e}")
            continue
    
    detector.camera.release()
    
    print(f"\n✅ Quick test completed!")
    print(f"📁 Check your photos in: {saves_dir}")
    print(f"💡 Look for files starting with 'detection_' to see face detection results")
    
    return True

def main():
    """Main function"""
    print("🎥 TRUE PRESENCE - HEADLESS CAMERA FACE DETECTION")
    print("=" * 60)
    print("💡 This version saves images instead of showing windows")
    print("   Perfect for your OpenCV installation!")
    
    print(f"\nChoose test mode:")
    print(f"1. Quick test (5 photos)")
    print(f"2. Extended test (30 seconds continuous)")
    print(f"3. Custom duration")
    
    try:
        choice = input(f"\nEnter choice (1-3) or press Enter for quick test: ").strip()
        
        if choice == "" or choice == "1":
            success = quick_camera_test()
        elif choice == "2":
            detector = HeadlessFaceDetection()
            success = detector.run_headless_detection(duration_seconds=30, save_interval=2)
        elif choice == "3":
            try:
                duration = int(input("Enter duration in seconds (default 30): ") or "30")
                interval = int(input("Enter save interval in seconds (default 2): ") or "2")
                detector = HeadlessFaceDetection()
                success = detector.run_headless_detection(duration_seconds=duration, save_interval=interval)
            except ValueError:
                print("Invalid input, using defaults...")
                detector = HeadlessFaceDetection()
                success = detector.run_headless_detection(duration_seconds=30, save_interval=2)
        else:
            print("Invalid choice, running quick test...")
            success = quick_camera_test()
        
        if success:
            print(f"\n✅ Camera test completed successfully!")
            print(f"🎯 Check the saved images to see your face detection results!")
            print(f"📂 Images are saved in:")
            print(f"   - quick_test_photos/ (for quick tests)")
            print(f"   - headless_captures/ (for extended tests)")
        else:
            print(f"\n❌ Camera test failed")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n👋 Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)