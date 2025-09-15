from django.contrib import admin
from .models import SystemMetric, SystemAlert


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    """Admin interface for SystemMetric model"""
    
    list_display = ('metric_type', 'value', 'unit', 'timestamp')
    list_filter = ('metric_type', 'timestamp')
    search_fields = ('metric_type',)
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    """Admin interface for SystemAlert model"""
    
    list_display = ('title', 'alert_type', 'severity', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_resolved', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'resolved_at')
    ordering = ('-created_at',)
    
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected alerts as resolved"""
        updated = queryset.update(is_resolved=True, resolved_by=request.user)
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_as_resolved.short_description = "Mark selected alerts as resolved"
