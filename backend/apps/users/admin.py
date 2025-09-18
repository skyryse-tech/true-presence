from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    list_display = ('employee_id', 'username', 'email', 'first_name', 'last_name', 
                   'role', 'department', 'face_enrolled', 'is_active', 'last_login')
    list_filter = ('role', 'department', 'face_enrolled', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('employee_id', 'username', 'email', 'first_name', 'last_name')
    ordering = ('employee_id',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Face Attendance Info', {
            'fields': ('employee_id', 'role', 'department', 'phone_number', 
                      'face_enrolled', 'enrollment_date', 'last_attendance')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Face Attendance Info', {
            'fields': ('employee_id', 'role', 'department', 'phone_number', 'face_enrolled')
        }),
    )
