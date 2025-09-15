from django.contrib import admin
from .models import FaceTemplate, FaceEnrollmentTask, FaceVerificationTask, FaceVerificationResult


@admin.register(FaceTemplate)
class FaceTemplateAdmin(admin.ModelAdmin):
    """Admin interface for FaceTemplate model"""
    
    list_display = ('user', 'quality_score', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__employee_id', 'user__first_name', 'user__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(FaceEnrollmentTask)
class FaceEnrollmentTaskAdmin(admin.ModelAdmin):
    """Admin interface for FaceEnrollmentTask model"""
    
    list_display = ('user', 'status', 'processing_time', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at', 'completed_at')
    search_fields = ('user__employee_id', 'user__first_name', 'user__last_name')
    readonly_fields = ('id', 'created_at', 'completed_at')
    ordering = ('-created_at',)


@admin.register(FaceVerificationTask)
class FaceVerificationTaskAdmin(admin.ModelAdmin):
    """Admin interface for FaceVerificationTask model"""
    
    list_display = ('id', 'camera_id', 'location', 'status', 'processing_time', 'created_at', 'completed_at')
    list_filter = ('status', 'camera_id', 'created_at', 'completed_at')
    search_fields = ('camera_id', 'location')
    readonly_fields = ('id', 'created_at', 'completed_at')
    ordering = ('-created_at',)


@admin.register(FaceVerificationResult)
class FaceVerificationResultAdmin(admin.ModelAdmin):
    """Admin interface for FaceVerificationResult model"""
    
    list_display = ('user', 'recognized', 'confidence', 'similarity_score', 'is_live', 'anti_spoof_score', 'created_at')
    list_filter = ('recognized', 'is_live', 'created_at')
    search_fields = ('user__employee_id', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
