from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Camera, CameraHealthLog, CameraEvent

User = get_user_model()


class CameraModelTest(TestCase):
    """Test cases for Camera model"""
    
    def setUp(self):
        self.camera = Camera.objects.create(
            id='CAM001',
            name='Main Entrance Camera',
            location='Building A - Ground Floor',
            camera_type='ip',
            ip_address='192.168.1.100',
            port=554,
            username='admin',
            password='password123'
        )
    
    def test_camera_creation(self):
        self.assertEqual(self.camera.id, 'CAM001')
        self.assertEqual(self.camera.name, 'Main Entrance Camera')
        self.assertEqual(self.camera.camera_type, 'ip')
        self.assertFalse(self.camera.is_online())
    
    def test_camera_str_representation(self):
        expected = 'Main Entrance Camera (CAM001)'
        self.assertEqual(str(self.camera), expected)
    
    def test_get_stream_url(self):
        expected_url = 'rtsp://admin:password123@192.168.1.100:554/stream'
        self.assertEqual(self.camera.get_stream_url(), expected_url)


class CameraAPITest(APITestCase):
    """Test cases for Camera API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001'
        )
        self.client.force_authenticate(user=self.user)
        
        self.camera = Camera.objects.create(
            id='CAM001',
            name='Test Camera',
            location='Test Location',
            camera_type='ip',
            ip_address='192.168.1.100'
        )
    
    def test_camera_list(self):
        url = reverse('cameras:camera-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_camera_detail(self):
        url = reverse('cameras:camera-detail', kwargs={'camera_id': 'CAM001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Camera')
    
    def test_camera_stream(self):
        url = reverse('cameras:camera-stream', kwargs={'camera_id': 'CAM001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stream_url', response.data)
    
    def test_camera_health(self):
        url = reverse('cameras:camera-health', kwargs={'camera_id': 'CAM001'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
    
    def test_camera_statistics(self):
        url = reverse('cameras:camera-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_cameras', response.data)
        self.assertEqual(response.data['total_cameras'], 1)
