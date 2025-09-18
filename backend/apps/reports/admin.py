from django.contrib import admin
from .models import ReportTemplate, ScheduledReport, ReportLog


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin interface for ReportTemplate model"""
    
    list_display = ('name', 'report_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('report_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    """Admin interface for ScheduledReport model"""
    
    list_display = ('name', 'template', 'frequency', 'is_active', 'last_run', 'next_run', 'created_by')
    list_filter = ('frequency', 'is_active', 'created_at')
    search_fields = ('name', 'template__name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'last_run')
    ordering = ('-created_at',)


@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    """Admin interface for ReportLog model"""
    
    list_display = ('report_id', 'template', 'status', 'generated_by', 'generated_at', 'completed_at')
    list_filter = ('status', 'template__report_type', 'generated_at')
    search_fields = ('report_id', 'template__name', 'generated_by__username')
    readonly_fields = ('report_id', 'generated_at', 'completed_at')
    ordering = ('-generated_at',)
