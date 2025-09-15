from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AttendanceLog(models.Model):
    """Attendance log for users"""
    
    ATTENDANCE_TYPES = [
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('break_start', 'Break Start'),
        ('break_end', 'Break End'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES, default='check_in')
    camera_id = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    verification_time = models.FloatField(null=True, blank=True)
    face_position = models.JSONField(null=True, blank=True)
    photo_path = models.CharField(max_length=500, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'attendance_logs'
        verbose_name = 'Attendance Log'
        verbose_name_plural = 'Attendance Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.attendance_type} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class AttendanceSummary(models.Model):
    """Daily attendance summary for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_summaries')
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    total_hours = models.FloatField(default=0.0)
    break_duration = models.FloatField(default=0.0)
    is_present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_summaries'
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date} ({'Present' if self.is_present else 'Absent'})"


class AttendanceRule(models.Model):
    """Attendance rules and policies"""
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    break_duration = models.IntegerField(default=60)  # in minutes
    late_tolerance = models.IntegerField(default=15)  # in minutes
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_rules'
        verbose_name = 'Attendance Rule'
        verbose_name_plural = 'Attendance Rules'
    
    def __str__(self):
        return self.name