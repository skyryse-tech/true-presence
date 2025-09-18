from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Attendance logs
    path('logs/', views.AttendanceLogListView.as_view(), name='attendance-logs'),
    path('logs/create/', views.AttendanceLogCreateView.as_view(), name='attendance-log-create'),
    
    # Attendance summaries and statistics
    path('summary/', views.AttendanceSummaryView.as_view(), name='attendance-summary'),
    path('stats/', views.attendance_stats, name='attendance-stats'),
    path('today/', views.today_attendance, name='today-attendance'),
    
    # Manual attendance
    path('mark/', views.mark_manual_attendance, name='mark-manual-attendance'),
    
    # User-specific attendance
    path('user/<str:employee_id>/', views.user_attendance_history, name='user-attendance-history'),
    
    # Attendance rules
    path('rules/', views.AttendanceRuleListView.as_view(), name='attendance-rules'),
    path('rules/<int:pk>/', views.AttendanceRuleDetailView.as_view(), name='attendance-rule-detail'),
]