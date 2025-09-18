from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, date, timedelta
from backend.apps.attendance.models import AttendanceLog, AttendanceSummary
from backend.apps.cameras.models import Camera, CameraEvent
from backend.apps.face_recognition.models import FaceVerificationTask
from .serializers import AttendanceReportSerializer, AnalyticsSerializer, PatternAnalysisSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_report(request):
    """Generate attendance report"""
    format_type = request.query_params.get('format', 'json')
    period = request.query_params.get('period', 'daily')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    department = request.query_params.get('department')
    employee_ids = request.query_params.get('employee_ids')
    
    # Set default date range if not provided
    if not date_from:
        if period == 'daily':
            date_from = date.today()
        elif period == 'weekly':
            date_from = date.today() - timedelta(days=7)
        elif period == 'monthly':
            date_from = date.today() - timedelta(days=30)
    
    if not date_to:
        date_to = date.today()
    
    # Build queryset
    queryset = AttendanceLog.objects.filter(
        timestamp__date__range=[date_from, date_to]
    )
    
    if department:
        queryset = queryset.filter(user__department__icontains=department)
    
    if employee_ids:
        employee_list = employee_ids.split(',')
        queryset = queryset.filter(user__employee_id__in=employee_list)
    
    # Calculate statistics
    total_employees = User.objects.count()
    total_attendances = queryset.count()
    unique_persons = queryset.values('user').distinct().count()
    attendance_rate = (unique_persons / total_employees * 100) if total_employees > 0 else 0
    
    # Department statistics
    dept_stats = {}
    if not department:
        dept_data = queryset.values('user__department').annotate(
            count=Count('id'),
            unique_users=Count('user', distinct=True)
        ).order_by('-count')
        dept_stats = {
            item['user__department'] or 'Unknown': {
                'total_attendances': item['count'],
                'unique_users': item['unique_users'],
                'attendance_rate': (item['unique_users'] / User.objects.filter(
                    department=item['user__department']
                ).count() * 100) if item['user__department'] else 0
            }
            for item in dept_data
        }
    
    report_data = {
        'report_id': f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'generated_at': timezone.now().isoformat(),
        'period': period,
        'date_range': f"{date_from} to {date_to}",
        'total_employees': total_employees,
        'total_attendances': total_attendances,
        'unique_persons': unique_persons,
        'attendance_rate': round(attendance_rate, 2),
        'department_stats': dept_stats
    }
    
    if format_type == 'json':
        serializer = AttendanceReportSerializer(report_data)
        return Response(serializer.data)
    else:
        # TODO: Implement PDF/Excel export
        return Response({'error': 'PDF/Excel export not implemented yet'}, 
                       status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def real_time_analytics(request):
    """Get real-time analytics dashboard data"""
    
    # Current occupancy (users who checked in today but haven't checked out)
    today = date.today()
    current_occupancy = AttendanceLog.objects.filter(
        timestamp__date=today,
        attendance_type='check_in'
    ).exclude(
        user__in=AttendanceLog.objects.filter(
            timestamp__date=today,
            attendance_type='check_out'
        ).values_list('user', flat=True)
    ).count()
    
    # Today's attendance
    today_attendance = AttendanceLog.objects.filter(
        timestamp__date=today
    ).count()
    
    # Peak hour analysis
    hourly_data = AttendanceLog.objects.filter(
        timestamp__date=today
    ).extra(
        select={'hour': 'EXTRACT(hour FROM timestamp)'}
    ).values('hour').annotate(count=Count('id')).order_by('-count')
    
    peak_hour = f"{hourly_data[0]['hour']:02d}:00" if hourly_data else "N/A"
    
    # Average processing time
    avg_processing_time = FaceVerificationTask.objects.filter(
        status='completed',
        completed_at__date=today
    ).aggregate(avg_time=Avg('processing_time'))['avg_time'] or 0
    
    # System health
    online_cameras = Camera.objects.filter(status='online').count()
    total_cameras = Camera.objects.count()
    recent_errors = CameraEvent.objects.filter(
        event_type='error',
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    analytics_data = {
        'current_occupancy': current_occupancy,
        'today_attendance': today_attendance,
        'peak_hour': peak_hour,
        'avg_processing_time': round(avg_processing_time, 2),
        'system_health': {
            'api_response_time': 0.15,  # Placeholder
            'ai_worker_status': 'healthy',  # Placeholder
            'database_connections': 45,  # Placeholder
            'queue_size': 12  # Placeholder
        },
        'camera_status': {
            'online': online_cameras,
            'offline': total_cameras - online_cameras,
            'errors': recent_errors
        }
    }
    
    serializer = AnalyticsSerializer(analytics_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def pattern_analysis(request):
    """Get attendance pattern analysis"""
    
    # Daily patterns (last 30 days)
    daily_patterns = {}
    for i in range(7):  # Days of week
        day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][i]
        day_attendances = AttendanceLog.objects.filter(
            timestamp__week_day=i+2,  # Django week_day: Sunday=1, Monday=2, etc.
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Get peak hour for this day
        peak_hour_data = AttendanceLog.objects.filter(
            timestamp__week_day=i+2,
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).extra(
            select={'hour': 'EXTRACT(hour FROM timestamp)'}
        ).values('hour').annotate(count=Count('id')).order_by('-count').first()
        
        peak_hour = f"{peak_hour_data['hour']:02d}:00" if peak_hour_data else "N/A"
        
        daily_patterns[day_name] = {
            'avg_attendance': day_attendances // 4,  # Approximate average over 4 weeks
            'peak_hour': peak_hour
        }
    
    # Seasonal trends (placeholder - would need more data)
    seasonal_trends = {
        'spring': 0.94,
        'summer': 0.67,
        'fall': 0.92,
        'winter': 0.89
    }
    
    # Predictions (placeholder)
    predictions = {
        'next_week_attendance': 18547,
        'confidence': 0.87
    }
    
    pattern_data = {
        'daily_patterns': daily_patterns,
        'seasonal_trends': seasonal_trends,
        'predictions': predictions
    }
    
    serializer = PatternAnalysisSerializer(pattern_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_report(request):
    """Export report in various formats"""
    format_type = request.query_params.get('format', 'json')
    report_type = request.query_params.get('type', 'attendance')
    
    if format_type not in ['json', 'pdf', 'excel']:
        return Response(
            {'error': 'Unsupported format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if format_type == 'json':
        # Return JSON data
        if report_type == 'attendance':
            return attendance_report(request)
        elif report_type == 'analytics':
            return real_time_analytics(request)
        elif report_type == 'patterns':
            return pattern_analysis(request)
        else:
            return Response(
                {'error': 'Unsupported report type'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        # TODO: Implement PDF/Excel export
        return Response(
            {'error': f'{format_type.upper()} export not implemented yet'}, 
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
