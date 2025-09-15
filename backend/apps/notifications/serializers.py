from rest_framework import serializers
from .models import Notification, NotificationTemplate, WebhookEndpoint


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'priority', 
                 'is_read', 'metadata', 'created_at', 'read_at']
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'title_template', 'message_template', 
                 'notification_type', 'priority', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for WebhookEndpoint model"""
    
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'name', 'url', 'secret_key', 'is_active', 'events', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }
