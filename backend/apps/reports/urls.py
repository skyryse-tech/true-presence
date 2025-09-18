from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report generation
    path('attendance/', views.attendance_report, name='attendance-report'),
    path('analytics/real-time/', views.real_time_analytics, name='real-time-analytics'),
    path('patterns/', views.pattern_analysis, name='pattern-analysis'),
    
    # Export functionality
    path('export/', views.export_report, name='export-report'),
]
