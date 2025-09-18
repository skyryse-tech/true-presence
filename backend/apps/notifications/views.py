from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification, NotificationTemplate, WebhookEndpoint
from .serializers import NotificationSerializer, NotificationTemplateSerializer, WebhookEndpointSerializer

User = get_user_model()


class NotificationListView(generics.ListAPIView):
    """List user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete notification"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all user notifications as read"""
    Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).update(
        is_read=True, 
        read_at=timezone.now()
    )
    return Response({'message': 'All notifications marked as read'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_notifications_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': count})


class NotificationTemplateListView(generics.ListCreateAPIView):
    """List and create notification templates"""
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(is_active=True)


class WebhookEndpointListView(generics.ListCreateAPIView):
    """List and create webhook endpoints"""
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WebhookEndpoint.objects.filter(is_active=True)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_test_notification(request):
    """Send a test notification"""
    title = request.data.get('title', 'Test Notification')
    message = request.data.get('message', 'This is a test notification')
    notification_type = request.data.get('type', 'system')
    priority = request.data.get('priority', 'medium')
    
    notification = Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        user=request.user
    )
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
