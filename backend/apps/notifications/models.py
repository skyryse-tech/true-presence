from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """Notification model for system alerts and messages"""
    
    NOTIFICATION_TYPES = [
        ('attendance', 'Attendance'),
        ('system', 'System'),
        ('security', 'Security'),
        ('maintenance', 'Maintenance'),
        ('alert', 'Alert'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"


class NotificationTemplate(models.Model):
    """Template for creating notifications"""
    
    name = models.CharField(max_length=100)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return self.name


class WebhookEndpoint(models.Model):
    """Webhook endpoints for external integrations"""
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    secret_key = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    events = models.JSONField(default=list)  # List of events to send
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_endpoints'
        verbose_name = 'Webhook Endpoint'
        verbose_name_plural = 'Webhook Endpoints'
    
    def __str__(self):
        return self.name
