from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class AdminDashboardAPITest(APITestCase):
    """Test cases for Admin Dashboard API endpoints"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            employee_id='ADMIN001'
        )
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001'
        )
    
    def test_dashboard_stats_admin_access(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_dashboard:dashboard-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('users', response.data)
        self.assertIn('attendance', response.data)
    
    def test_dashboard_stats_regular_user_denied(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('admin_dashboard:dashboard-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_system_health_admin_access(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_dashboard:system-health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('services', response.data)
    
    def test_recent_activity_admin_access(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_dashboard:recent-activity')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attendance', response.data)
        self.assertIn('camera_events', response.data)
