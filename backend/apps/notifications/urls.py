from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('unread-count/', views.unread_notifications_count, name='unread-notifications-count'),
    
    # Templates
    path('templates/', views.NotificationTemplateListView.as_view(), name='notification-template-list'),
    
    # Webhooks
    path('webhooks/', views.WebhookEndpointListView.as_view(), name='webhook-endpoint-list'),
    
    # Test
    path('test/', views.send_test_notification, name='send-test-notification'),
]
