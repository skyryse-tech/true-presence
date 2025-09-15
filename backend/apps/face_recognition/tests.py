from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import FaceTemplate, FaceEnrollmentTask, FaceVerificationTask, FaceVerificationResult

User = get_user_model()


class FaceRecognitionModelTest(TestCase):
    """Test cases for Face Recognition models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User'
        )
    
    def test_face_template_creation(self):
        template = FaceTemplate.objects.create(
            user=self.user,
            template_data=b'test_template_data',
            quality_score=0.95
        )
        self.assertEqual(template.user, self.user)
        self.assertEqual(template.quality_score, 0.95)
        self.assertTrue(template.is_active)
    
    def test_enrollment_task_creation(self):
        task = FaceEnrollmentTask.objects.create(
            user=self.user,
            images=['image1', 'image2', 'image3'],
            status='queued'
        )
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, 'queued')
        self.assertEqual(len(task.images), 3)
    
    def test_verification_task_creation(self):
        task = FaceVerificationTask.objects.create(
            image='base64_image_data',
            camera_id='CAM001',
            status='queued'
        )
        self.assertEqual(task.camera_id, 'CAM001')
        self.assertEqual(task.status, 'queued')


class FaceRecognitionAPITest(APITestCase):
    """Test cases for Face Recognition API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_face_enrollment(self):
        url = reverse('face_recognition:face-enroll')
        data = {
            'employee_id': 'EMP001',
            'images': ['image1', 'image2', 'image3'],
            'quality_check': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], 'completed')
    
    def test_face_verification(self):
        url = reverse('face_recognition:face-verify')
        data = {
            'image': 'base64_image_data',
            'camera_id': 'CAM001',
            'location': 'Main Entrance'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
    
    def test_enrollment_status(self):
        # Create an enrollment task
        task = FaceEnrollmentTask.objects.create(
            user=self.user,
            images=['image1', 'image2', 'image3'],
            status='completed'
        )
        
        url = reverse('face_recognition:enrollment-status', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
    
    def test_verification_status(self):
        # Create a verification task
        task = FaceVerificationTask.objects.create(
            image='base64_image_data',
            status='completed'
        )
        
        url = reverse('face_recognition:verification-status', kwargs={'task_id': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
