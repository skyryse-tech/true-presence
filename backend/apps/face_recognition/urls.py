from django.urls import path
from . import views

app_name = 'face_recognition'

urlpatterns = [
    # Face enrollment endpoints
    path('enroll/', views.FaceEnrollmentView.as_view(), name='face-enroll'),
    path('enroll/status/<uuid:task_id>/', views.FaceEnrollmentStatusView.as_view(), name='enrollment-status'),
    
    # Face verification endpoints
    path('verify/', views.FaceVerificationView.as_view(), name='face-verify'),
    path('verify/status/<uuid:task_id>/', views.FaceVerificationStatusView.as_view(), name='verification-status'),
    path('bulk-verify/', views.BulkVerificationView.as_view(), name='bulk-verify'),
    
    # Face template endpoints
    path('templates/', views.FaceTemplateListView.as_view(), name='face-templates'),
    
    # Alternative status endpoints (for compatibility)
    path('enroll/status/<uuid:task_id>/', views.enrollment_status, name='enrollment-status-alt'),
    path('verify/status/<uuid:task_id>/', views.verification_status, name='verification-status-alt'),
]
