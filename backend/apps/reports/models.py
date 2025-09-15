from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportTemplate(models.Model):
    """Report templates for different types of reports"""
    
    REPORT_TYPES = [
        ('attendance', 'Attendance Report'),
        ('analytics', 'Analytics Report'),
        ('patterns', 'Pattern Analysis'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    template_config = models.JSONField()  # Store template configuration
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_templates'
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
    
    def __str__(self):
        return self.name


class ScheduledReport(models.Model):
    """Scheduled reports for automatic generation"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    name = models.CharField(max_length=100)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='scheduled_reports')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    recipients = models.JSONField()  # List of email addresses
    parameters = models.JSONField(default=dict)  # Report parameters
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_reports'
        verbose_name = 'Scheduled Report'
        verbose_name_plural = 'Scheduled Reports'
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"


class ReportLog(models.Model):
    """Log of generated reports"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    report_id = models.CharField(max_length=50, unique=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='report_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    parameters = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'report_logs'
        verbose_name = 'Report Log'
        verbose_name_plural = 'Report Logs'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_id} - {self.template.name} ({self.status})"
