from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class FaceTemplate(models.Model):
    """Face template for enrolled users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='face_template')
    template_data = models.BinaryField()  # Encrypted face encoding
    quality_score = models.FloatField(default=0.0)
    enrollment_images = models.JSONField(default=list)  # Store image metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'face_templates'
        verbose_name = 'Face Template'
        verbose_name_plural = 'Face Templates'
    
    def __str__(self):
        return f"Face Template for {self.user.get_full_name()}"


class FaceEnrollmentTask(models.Model):
    """Task tracking for face enrollment"""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollment_tasks')
    images = models.JSONField()  # Base64 encoded images
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    result = models.JSONField(null=True, blank=True)  # Processing result
    error_message = models.TextField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'face_enrollment_tasks'
        verbose_name = 'Face Enrollment Task'
        verbose_name_plural = 'Face Enrollment Tasks'
    
    def __str__(self):
        return f"Enrollment Task for {self.user.get_full_name()} - {self.status}"


class FaceVerificationTask(models.Model):
    """Task tracking for face verification"""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.TextField()  # Base64 encoded image
    camera_id = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    result = models.JSONField(null=True, blank=True)  # Verification result
    error_message = models.TextField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'face_verification_tasks'
        verbose_name = 'Face Verification Task'
        verbose_name_plural = 'Face Verification Tasks'
    
    def __str__(self):
        return f"Verification Task - {self.status}"


class FaceVerificationResult(models.Model):
    """Result of face verification"""
    
    task = models.OneToOneField(FaceVerificationTask, on_delete=models.CASCADE, related_name='verification_result')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='verification_results')
    recognized = models.BooleanField(default=False)
    confidence = models.FloatField(default=0.0)
    similarity_score = models.FloatField(default=0.0)
    is_live = models.BooleanField(default=False)
    anti_spoof_score = models.FloatField(default=0.0)
    face_quality = models.FloatField(default=0.0)
    face_position = models.JSONField(null=True, blank=True)  # Face coordinates
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'face_verification_results'
        verbose_name = 'Face Verification Result'
        verbose_name_plural = 'Face Verification Results'
    
    def __str__(self):
        if self.recognized and self.user:
            return f"Verified: {self.user.get_full_name()} ({self.confidence:.2%})"
        return f"Verification: {'Recognized' if self.recognized else 'Unknown'} ({self.confidence:.2%})"
