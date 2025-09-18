from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Extended User model for face attendance system"""
    
    ROLES = [
        ('admin', 'Administrator'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
        ('staff', 'Staff'),
    ]
    
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='student')
    department = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    face_enrolled = models.BooleanField(default=False)
    enrollment_date = models.DateTimeField(null=True, blank=True)
    last_attendance = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def has_face_enrolled(self):
        return self.face_enrolled and self.enrollment_date is not None
    
    def get_attendance_count(self):
        return self.attendance_logs.count()
    
    def get_last_attendance_date(self):
        last_attendance = self.attendance_logs.order_by('-timestamp').first()
        return last_attendance.timestamp if last_attendance else None
