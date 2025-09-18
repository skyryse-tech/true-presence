from django.contrib import admin
from .models import Notification, NotificationTemplate, WebhookEndpoint


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    
    list_display = ('title', 'notification_type', 'priority', 'user', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__employee_id')
    readonly_fields = ('created_at', 'read_at')
    ordering = ('-created_at',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for NotificationTemplate model"""
    
    list_display = ('name', 'notification_type', 'priority', 'is_active', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_active', 'created_at')
    search_fields = ('name', 'title_template', 'message_template')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    """Admin interface for WebhookEndpoint model"""
    
    list_display = ('name', 'url', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'url')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
