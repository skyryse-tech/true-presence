from django.contrib import admin
from .models import AttendanceLog, AttendanceSummary, AttendanceRule


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceLog model"""
    
    list_display = ('user', 'timestamp', 'attendance_type', 'camera_id', 'location', 'confidence')
    list_filter = ('attendance_type', 'timestamp', 'camera_id')
    search_fields = ('user__employee_id', 'user__first_name', 'user__last_name', 'camera_id', 'location')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceSummary model"""
    
    list_display = ('user', 'date', 'check_in_time', 'check_out_time', 'total_hours', 'is_present')
    list_filter = ('date', 'is_present')
    search_fields = ('user__employee_id', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date',)


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    """Admin interface for AttendanceRule model"""
    
    list_display = ('name', 'check_in_time', 'check_out_time', 'break_duration', 'late_tolerance', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)