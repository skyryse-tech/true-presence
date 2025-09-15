from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('health/', views.system_health, name='system-health'),
    path('activity/', views.recent_activity, name='recent-activity'),
    
    # Maintenance
    path('maintenance/', views.system_maintenance, name='system-maintenance'),
]
