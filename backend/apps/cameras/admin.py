from django.contrib import admin
from .models import Camera, CameraHealthLog, CameraEvent


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    """Admin interface for Camera model"""
    
    list_display = ('id', 'name', 'location', 'camera_type', 'ip_address', 'status', 'is_active', 'last_seen')
    list_filter = ('camera_type', 'status', 'is_active', 'created_at')
    search_fields = ('id', 'name', 'location', 'ip_address')
    readonly_fields = ('created_at', 'updated_at', 'last_seen')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'location', 'camera_type')
        }),
        ('Connection Details', {
            'fields': ('ip_address', 'rtsp_url', 'username', 'password', 'port')
        }),
        ('Settings', {
            'fields': ('resolution', 'fps', 'is_active')
        }),
        ('Status', {
            'fields': ('status', 'last_seen')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CameraHealthLog)
class CameraHealthLogAdmin(admin.ModelAdmin):
    """Admin interface for CameraHealthLog model"""
    
    list_display = ('camera', 'status', 'quality_score', 'error_count', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('camera__name', 'camera__id', 'error_message')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(CameraEvent)
class CameraEventAdmin(admin.ModelAdmin):
    """Admin interface for CameraEvent model"""
    
    list_display = ('camera', 'event_type', 'severity', 'is_resolved', 'timestamp')
    list_filter = ('event_type', 'severity', 'is_resolved', 'timestamp')
    search_fields = ('camera__name', 'camera__id', 'message')
    readonly_fields = ('timestamp', 'resolved_at')
    ordering = ('-timestamp',)
    
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected events as resolved"""
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f'{updated} events marked as resolved.')
    mark_as_resolved.short_description = "Mark selected events as resolved"
