from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Notification, NotificationTemplate

User = get_user_model()


class NotificationsAPITest(APITestCase):
    """Test cases for Notifications API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP001'
        )
        self.client.force_authenticate(user=self.user)
        
        self.notification = Notification.objects.create(
            title='Test Notification',
            message='This is a test notification',
            notification_type='system',
            priority='medium',
            user=self.user
        )
    
    def test_notification_list(self):
        url = reverse('notifications:notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_mark_notification_read(self):
        url = reverse('notifications:mark-notification-read', kwargs={'notification_id': self.notification.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if notification is marked as read
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
    
    def test_unread_notifications_count(self):
        url = reverse('notifications:unread-notifications-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)
