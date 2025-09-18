from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/auth/', include('backend.apps.authentication.urls')),
    path('api/v1/users/', include('backend.apps.users.urls')),
    path('api/v1/attendance/', include('backend.apps.attendance.urls')),
    path('api/v1/face/', include('backend.apps.face_recognition.urls')),
    path('api/v1/cameras/', include('backend.apps.cameras.urls')),
    path('api/v1/reports/', include('backend.apps.reports.urls')),
    path('api/v1/notifications/', include('backend.apps.notifications.urls')),
    path('api/v1/admin/', include('backend.apps.admin_dashboard.urls')),
    
    # Health check endpoint
    path('health/', include('django_health_check.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
