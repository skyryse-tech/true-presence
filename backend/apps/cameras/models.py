from django.db import models
from django.utils import timezone


class Camera(models.Model):
    """Camera model for managing surveillance cameras"""
    
    CAMERA_TYPES = [
        ('ip', 'IP Camera'),
        ('usb', 'USB Camera'),
        ('rtsp', 'RTSP Stream'),
        ('webcam', 'Webcam'),
    ]
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    camera_type = models.CharField(max_length=20, choices=CAMERA_TYPES, default='ip')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    rtsp_url = models.URLField(null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    port = models.IntegerField(default=554)
    resolution = models.CharField(max_length=20, default='1920x1080')
    fps = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cameras'
        verbose_name = 'Camera'
        verbose_name_plural = 'Cameras'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.id})"
    
    def is_online(self):
        return self.status == 'online'
    
    def get_stream_url(self):
        """Get the stream URL for the camera"""
        if self.camera_type == 'rtsp' and self.rtsp_url:
            return self.rtsp_url
        elif self.camera_type == 'ip' and self.ip_address:
            auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
            return f"rtsp://{auth}{self.ip_address}:{self.port}/stream"
        return None


class CameraHealthLog(models.Model):
    """Camera health monitoring log"""
    
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='health_logs')
    status = models.CharField(max_length=20, choices=Camera.STATUS_CHOICES)
    uptime = models.DurationField(null=True, blank=True)
    last_frame = models.DateTimeField(null=True, blank=True)
    quality_score = models.FloatField(default=0.0)
    bandwidth_usage = models.CharField(max_length=50, null=True, blank=True)
    error_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'camera_health_logs'
        verbose_name = 'Camera Health Log'
        verbose_name_plural = 'Camera Health Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.camera.name} - {self.status} at {self.timestamp}"


class CameraEvent(models.Model):
    """Camera events and alerts"""
    
    EVENT_TYPES = [
        ('motion', 'Motion Detected'),
        ('face_detected', 'Face Detected'),
        ('attendance', 'Attendance Marked'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'camera_events'
        verbose_name = 'Camera Event'
        verbose_name_plural = 'Camera Events'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.camera.name} - {self.event_type} ({self.severity})"
