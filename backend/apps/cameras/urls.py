from django.urls import path
from . import views

app_name = 'cameras'

urlpatterns = [
    # Camera management
    path('', views.CameraListView.as_view(), name='camera-list'),
    path('<str:camera_id>/', views.CameraDetailView.as_view(), name='camera-detail'),
    
    # Camera operations
    path('<str:camera_id>/stream/', views.camera_stream, name='camera-stream'),
    path('<str:camera_id>/test/', views.test_camera_connection, name='camera-test'),
    path('<str:camera_id>/health/', views.camera_health, name='camera-health'),
    path('<str:camera_id>/status/', views.update_camera_status, name='camera-status'),
    
    # Camera monitoring
    path('<str:camera_id>/health-logs/', views.CameraHealthLogListView.as_view(), name='camera-health-logs'),
    path('<str:camera_id>/events/', views.CameraEventListView.as_view(), name='camera-events'),
    
    # Statistics
    path('statistics/', views.camera_statistics, name='camera-statistics'),
]
