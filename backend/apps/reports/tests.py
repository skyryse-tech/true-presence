from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import ReportTemplate, ScheduledReport, ReportLog

User = get_user_model()


class ReportsAPITest(APITestCase):
    """Test cases for Reports API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_attendance_report(self):
        url = reverse('reports:attendance-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('report_id', response.data)
        self.assertIn('total_employees', response.data)
    
    def test_real_time_analytics(self):
        url = reverse('reports:real-time-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current_occupancy', response.data)
        self.assertIn('system_health', response.data)
    
    def test_pattern_analysis(self):
        url = reverse('reports:pattern-analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_patterns', response.data)
        self.assertIn('predictions', response.data)
