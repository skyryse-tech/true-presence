from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User',
            role='faculty',
            department='Computer Science'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.employee_id, 'EMP001')
        self.assertEqual(self.user.role, 'faculty')
        self.assertFalse(self.user.face_enrolled)
    
    def test_user_str_representation(self):
        expected = 'Test User (EMP001)'
        self.assertEqual(str(self.user), expected)
    
    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Test User')


class UserAPITest(APITestCase):
    """Test cases for User API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001',
            first_name='Test',
            last_name='User',
            role='faculty'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            employee_id='ADMIN001'
        )
    
    def test_user_login(self):
        url = reverse('users:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_user_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'EMP001')
    
    def test_user_list_requires_authentication(self):
        url = reverse('users:user-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
