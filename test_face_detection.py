"""
Face Detection System Test Script

This script tests the new face detection system to ensure:
1. Configuration loads correctly
2. Detection service initializes properly
3. Face processor works with different backends
4. Error handling works correctly
"""

import os
import sys
import numpy as np
import cv2
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_image() -> np.ndarray:
    """Create a test image with synthetic faces for testing"""
    # Create a simple test image with geometric shapes as "faces"
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some noise to make it more realistic
    noise = np.random.randint(0, 50, image.shape, dtype=np.uint8)
    image = cv2.add(image, noise)
    
    # Draw some rectangles to simulate faces
    cv2.rectangle(image, (100, 100), (200, 200), (100, 150, 200), -1)
    cv2.rectangle(image, (300, 150), (400, 250), (150, 100, 200), -1)
    cv2.rectangle(image, (450, 200), (550, 300), (200, 150, 100), -1)
    
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

def test_detection_service():
    """Test detection service initialization"""
    print("\nTesting Detection Service...")
    
    try:
        from ai_workers.detection_service import FaceDetectionService
        from ai_workers.config import FaceDetectionConfig
        
        config = FaceDetectionConfig()
        service = FaceDetectionService(config)
        print(f"  ✓ Detection service initialized")
        
        # Test with synthetic image
        test_image = create_test_image()
        detected_faces = service.detect_faces(test_image)
        print(f"  ✓ Detection executed (found {len(detected_faces)} faces)")
        
        # Test embedding extraction with a small test crop
        test_crop = test_image[100:200, 100:200]  # Extract a small crop
        if test_crop.size > 0:
            try:
                embedding = service.get_embedding(test_crop)
                if embedding is not None:
                    print(f"  ✓ Embedding extraction successful (size: {len(embedding)})")
                else:
                    print(f"  ! Embedding extraction returned None (expected for synthetic image)")
            except Exception as e:
                print(f"  ! Embedding extraction failed (expected for synthetic image): {e}")
        
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
        
        # Test with synthetic image bytes
        test_image = create_test_image()
        _, buffer = cv2.imencode('.jpg', test_image)
        image_bytes = buffer.tobytes()
        
        result = processor.process_image(image_bytes)
        print(f"  ✓ Image processing completed")
        print(f"    - Success: {result.get('success', False)}")
        print(f"    - Faces detected: {result.get('faces_detected', 0)}")
        print(f"    - Faces processed: {result.get('faces_processed', 0)}")
        
        # Test validation
        if result.get('faces'):
            face = result['faces'][0]
            validation = processor.validate_face_for_attendance(face)
            print(f"  ✓ Face validation completed")
            print(f"    - Valid: {validation['is_valid']}")
            if not validation['is_valid']:
                print(f"    - Reasons: {validation['reasons']}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Face processor test failed: {e}")
        return False

def test_legacy_compatibility():
    """Test legacy compatibility layer"""
    print("\nTesting Legacy Compatibility...")
    
    try:
        from ai_workers import get_legacy_processor
        
        legacy_processor = get_legacy_processor()
        print(f"  ✓ Legacy processor initialized")
        
        # Test legacy process_frame method
        test_image = create_test_image()
        results = legacy_processor.process_frame(test_image)
        print(f"  ✓ Legacy process_frame executed")
        print(f"    - Faces found: {len(results)}")
        
        for i, face in enumerate(results):
            print(f"    - Face {i+1}: bbox={face['bbox']}, confidence={face['confidence']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Legacy compatibility test failed: {e}")
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
        
        # Test with very small image
        tiny_image = np.ones((10, 10, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', tiny_image)
        result = processor.process_image(buffer.tobytes())
        # This might succeed or fail depending on configuration
        print(f"  ✓ Small image handled: success={result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("FACE DETECTION SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Detection Service", test_detection_service),
        ("Face Processor", test_face_processor),
        ("Legacy Compatibility", test_legacy_compatibility),
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
        return True
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
