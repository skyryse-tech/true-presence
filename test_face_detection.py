"""
Face Detection System Test Script

This script tests the face detection system with real photos:
1. Configuration loads correctly
2. Detection service initializes properly
3. Face processor works with real photos
4. Tests with your actual photos (straight, left, right face)
"""

import os
import sys
import numpy as np
import cv2
from typing import Dict, Any, List
from pathlib import Path

# Fix: Add the current directory to the path (not parent)
project_root = Path(__file__).parent  # ✅ Current directory
sys.path.insert(0, str(project_root))

def create_test_photo_structure():
    """Create test photo directory structure"""
    test_dir = Path(__file__).parent / "test_photos" / "person1"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    return test_dir

def get_test_photos() -> List[Path]:
    """Get list of test photos"""
    test_dir = create_test_photo_structure()
    
    photo_names = ['straight.jpg', 'left.jpg', 'right.jpg', 
                   'straight.png', 'left.png', 'right.png',
                   'front.jpg', 'profile_left.jpg', 'profile_right.jpg']
    
    found_photos = []
    for photo_name in photo_names:
        photo_path = test_dir / photo_name
        if photo_path.exists():
            found_photos.append(photo_path)
    
    # Also check for any jpg/png files in the directory
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        found_photos.extend(test_dir.glob(ext))
    
    # Remove duplicates
    found_photos = list(set(found_photos))
    
    return found_photos

def create_test_image() -> np.ndarray:
    """Create a test image with synthetic faces for testing (fallback)"""
    # Create a simple test image with geometric shapes as "faces"
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some noise to make it more realistic
    noise = np.random.randint(0, 50, image.shape, dtype=np.uint8)
    image = cv2.add(image, noise)
    
    # Draw some rectangles to simulate faces
    cv2.rectangle(image, (100, 100), (200, 200), (100, 150, 200), -1)
    cv2.rectangle(image, (300, 150), (400, 250), (150, 100, 200), -1)
    
    # Add some circles for eyes
    cv2.circle(image, (130, 130), 10, (255, 255, 255), -1)
    cv2.circle(image, (170, 130), 10, (255, 255, 255), -1)
    cv2.circle(image, (330, 180), 10, (255, 255, 255), -1)
    cv2.circle(image, (370, 180), 10, (255, 255, 255), -1)
    
    return image

def test_configuration():
    """Test configuration loading"""
    print("Testing Configuration...")
    
    try:
        from ai_workers.config import FaceDetectionConfig, DetectorBackend, RecognitionModel
        
        # Test default configuration
        config = FaceDetectionConfig()
        print(f"  ✓ Default config loaded")
        print(f"    - Detector: {config.detector_backend}")
        print(f"    - Model: {config.recognition_model}")
        print(f"    - Target size: {config.target_size}")
        
        # Test environment loading (should use defaults if no env vars)
        env_config = FaceDetectionConfig.from_env()
        print(f"  ✓ Environment config loaded")
        
        # Test configuration validation
        assert config.min_detection_confidence > 0
        assert config.recognition_threshold > 0
        assert config.min_face_size > 0
        print(f"  ✓ Configuration validation passed")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False

def test_with_real_photos():
    """Test with real photos"""
    print("\nTesting with Real Photos...")
    
    test_photos = get_test_photos()
    
    if not test_photos:
        test_dir = create_test_photo_structure()
        print(f"  ⚠️  No test photos found in {test_dir}")
        print("  📋 Instructions:")
        print(f"     1. Add your photos to: {test_dir}")
        print("     2. Recommended names: straight.jpg, left.jpg, right.jpg")
        print("     3. Or use any .jpg/.png files")
        print("     4. Run this script again")
        return False
    
    print(f"  📸 Found {len(test_photos)} test photos:")
    for photo in test_photos:
        print(f"     - {photo.name}")
    
    try:
        from ai_workers import get_face_processor
        
        processor = get_face_processor()
        print(f"  ✓ Face processor initialized")
        
        results = {}
        
        for photo_path in test_photos:
            print(f"\n  🔍 Testing: {photo_path.name}")
            
            try:
                # Read image file
                with open(photo_path, 'rb') as f:
                    image_bytes = f.read()
                
                # Process image
                result = processor.process_image(image_bytes)
                
                print(f"     ✓ Processing completed")
                print(f"     - Success: {result.get('success', False)}")
                print(f"     - Faces detected: {result.get('faces_detected', 0)}")
                print(f"     - Processing time: {result.get('processing_time', 0):.2f}s")
                
                if result.get('faces'):
                    face = result['faces'][0]
                    print(f"     - Confidence: {face.get('confidence', 0):.3f}")
                    print(f"     - Quality score: {face.get('quality', {}).get('quality_score', 0):.3f}")
                    
                    # Test face validation
                    validation = processor.validate_face_for_attendance(face)
                    print(f"     - Valid for attendance: {validation.get('is_valid', False)}")
                    if not validation.get('is_valid', True):
                        print(f"     - Issues: {', '.join(validation.get('reasons', []))}")
                
                results[photo_path.name] = result
                
            except Exception as e:
                print(f"     ✗ Failed to process {photo_path.name}: {e}")
                results[photo_path.name] = {'success': False, 'error': str(e)}
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('success', False))
        print(f"\n  📊 Summary: {successful}/{len(test_photos)} photos processed successfully")
        
        return successful > 0
        
    except Exception as e:
        print(f"  ✗ Real photo test failed: {e}")
        return False

def test_detection_service():
    """Test detection service initialization"""
    print("\nTesting Detection Service...")
    
    try:
        from ai_workers.detection_service import FaceDetectionService
        from ai_workers.config import FaceDetectionConfig
        
        config = FaceDetectionConfig()
        service = FaceDetectionService(config)
        print(f"  ✓ Detection service initialized")
        
        # Test with synthetic image (fallback)
        test_image = create_test_image()
        detected_faces = service.detect_faces(test_image)
        print(f"  ✓ Detection executed (found {len(detected_faces)} faces)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Detection service test failed: {e}")
        return False

def test_face_processor():
    """Test the main face processor"""
    print("\nTesting Face Processor...")
    
    try:
        from ai_workers import get_face_processor
        
        processor = get_face_processor()
        print(f"  ✓ Face processor initialized")
        
        # Get system info
        info = processor.get_system_info()
        print(f"  ✓ System info retrieved")
        print(f"    - Recognition model: {info['processor_config']['recognition_model']}")
        print(f"    - Detector backend: {info['processor_config']['detector_backend']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Face processor test failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\nTesting Error Handling...")
    
    try:
        from ai_workers import get_face_processor
        
        processor = get_face_processor()
        
        # Test with empty bytes
        result = processor.process_image(b"")
        assert not result.get('success', True), "Should fail with empty input"
        print(f"  ✓ Empty input handled correctly")
        
        # Test with invalid image bytes
        result = processor.process_image(b"invalid image data")
        assert not result.get('success', True), "Should fail with invalid input"
        print(f"  ✓ Invalid input handled correctly")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False

def show_instructions():
    """Show setup instructions"""
    test_dir = create_test_photo_structure()
    
    print("\n" + "=" * 60)
    print("📋 SETUP INSTRUCTIONS")
    print("=" * 60)
    print(f"Test photo directory: {test_dir}")
    print("\n📸 Add your photos with these suggestions:")
    print("   - straight.jpg (front-facing photo)")
    print("   - left.jpg (left profile)")
    print("   - right.jpg (right profile)")
    print("\n💡 Photo tips:")
    print("   - Clear, well-lit photos")
    print("   - Face should be 20-80% of image")
    print("   - Good resolution (at least 640x480)")
    print("   - JPG or PNG format")
    print("\n🚀 After adding photos, run this script again!")

def main():
    """Run all tests"""
    print("=" * 60)
    print("FACE DETECTION SYSTEM TEST SUITE")
    print("=" * 60)
    
    # Check if photos exist first
    test_photos = get_test_photos()
    
    if not test_photos:
        show_instructions()
        return False
    
    tests = [
        ("Configuration", test_configuration),
        ("Face Processor", test_face_processor),
        ("Detection Service", test_detection_service),
        ("Real Photos", test_with_real_photos),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name} test PASSED")
            else:
                print(f"\n✗ {test_name} test FAILED")
        except Exception as e:
            print(f"\n✗ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! Face detection system is working correctly.")
        print("\n📋 Next steps:")
        print("   - Try adding more photos for better recognition")
        print("   - Test the attendance enrollment process")
        print("   - Set up the full Django application")
        return True
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
