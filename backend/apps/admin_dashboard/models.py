from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SystemMetric(models.Model):
    """System performance metrics"""
    
    METRIC_TYPES = [
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('disk', 'Disk Usage'),
        ('network', 'Network I/O'),
        ('api_response', 'API Response Time'),
        ('face_processing', 'Face Processing Time'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='%')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'system_metrics'
        verbose_name = 'System Metric'
        verbose_name_plural = 'System Metrics'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}{self.unit}"


class SystemAlert(models.Model):
    """System alerts and warnings"""
    
    ALERT_TYPES = [
        ('performance', 'Performance'),
        ('security', 'Security'),
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Information'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_alerts'
        verbose_name = 'System Alert'
        verbose_name_plural = 'System Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
