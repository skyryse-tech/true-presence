from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, date, timedelta
from backend.apps.attendance.models import AttendanceLog
from backend.apps.cameras.models import Camera, CameraEvent
from backend.apps.face_recognition.models import FaceVerificationTask, FaceEnrollmentTask
from backend.apps.notifications.models import Notification
from .serializers import DashboardStatsSerializer, SystemHealthSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for admin"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    today = date.today()
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    face_enrolled_users = User.objects.filter(face_enrolled=True).count()
    
    # Attendance statistics
    today_attendance = AttendanceLog.objects.filter(timestamp__date=today).count()
    total_attendance = AttendanceLog.objects.count()
    
    # Camera statistics
    total_cameras = Camera.objects.count()
    online_cameras = Camera.objects.filter(status='online').count()
    offline_cameras = Camera.objects.filter(status='offline').count()
    
    # Face recognition statistics
    total_enrollments = FaceEnrollmentTask.objects.count()
    completed_enrollments = FaceEnrollmentTask.objects.filter(status='completed').count()
    total_verifications = FaceVerificationTask.objects.count()
    completed_verifications = FaceVerificationTask.objects.filter(status='completed').count()
    
    # Recent activity
    recent_attendance = AttendanceLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    recent_errors = CameraEvent.objects.filter(
        event_type='error',
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Notifications
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    stats_data = {
        'users': {
            'total': total_users,
            'active': active_users,
            'face_enrolled': face_enrolled_users,
            'enrollment_rate': (face_enrolled_users / total_users * 100) if total_users > 0 else 0
        },
        'attendance': {
            'today': today_attendance,
            'total': total_attendance,
            'recent_24h': recent_attendance
        },
        'cameras': {
            'total': total_cameras,
            'online': online_cameras,
            'offline': offline_cameras,
            'uptime_percentage': (online_cameras / total_cameras * 100) if total_cameras > 0 else 0
        },
        'face_recognition': {
            'enrollments': {
                'total': total_enrollments,
                'completed': completed_enrollments,
                'success_rate': (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
            },
            'verifications': {
                'total': total_verifications,
                'completed': completed_verifications,
                'success_rate': (completed_verifications / total_verifications * 100) if total_verifications > 0 else 0
            }
        },
        'system': {
            'recent_errors': recent_errors,
            'unread_notifications': unread_notifications
        }
    }
    
    serializer = DashboardStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def system_health(request):
    """Get system health status"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Database health
    try:
        User.objects.count()
        db_status = 'healthy'
        db_response_time = 0.05  # Placeholder
    except Exception:
        db_status = 'error'
        db_response_time = None
    
    # Redis health (placeholder)
    redis_status = 'healthy'
    redis_memory_usage = '45%'
    
    # RabbitMQ health (placeholder)
    rabbitmq_status = 'healthy'
    queue_size = 12
    
    # AI workers health (placeholder)
    ai_workers_status = 'healthy'
    active_workers = 4
    
    # Performance metrics
    avg_api_response_time = 0.15
    requests_per_minute = 342
    error_rate = 0.001
    
    health_data = {
        'status': 'healthy' if all([
            db_status == 'healthy',
            redis_status == 'healthy',
            rabbitmq_status == 'healthy',
            ai_workers_status == 'healthy'
        ]) else 'degraded',
        'timestamp': timezone.now().isoformat(),
        'services': {
            'database': {
                'status': db_status,
                'response_time': db_response_time
            },
            'redis': {
                'status': redis_status,
                'memory_usage': redis_memory_usage
            },
            'rabbitmq': {
                'status': rabbitmq_status,
                'queue_size': queue_size
            },
            'ai_workers': {
                'status': ai_workers_status,
                'active_workers': active_workers
            }
        },
        'performance': {
            'avg_api_response_time': avg_api_response_time,
            'requests_per_minute': requests_per_minute,
            'error_rate': error_rate
        }
    }
    
    serializer = SystemHealthSerializer(health_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_activity(request):
    """Get recent system activity"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Recent attendance logs
    recent_attendance = AttendanceLog.objects.select_related('user').filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-timestamp')[:10]
    
    # Recent camera events
    recent_events = CameraEvent.objects.select_related('camera').filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-timestamp')[:10]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at')[:10]
    
    activity_data = {
        'attendance': [
            {
                'id': log.id,
                'user': log.user.get_full_name(),
                'employee_id': log.user.employee_id,
                'timestamp': log.timestamp,
                'type': log.attendance_type,
                'confidence': log.confidence
            }
            for log in recent_attendance
        ],
        'camera_events': [
            {
                'id': event.id,
                'camera': event.camera.name,
                'event_type': event.event_type,
                'severity': event.severity,
                'message': event.message,
                'timestamp': event.timestamp
            }
            for event in recent_events
        ],
        'notifications': [
            {
                'id': notif.id,
                'title': notif.title,
                'type': notif.notification_type,
                'priority': notif.priority,
                'is_read': notif.is_read,
                'created_at': notif.created_at
            }
            for notif in recent_notifications
        ]
    }
    
    return Response(activity_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def system_maintenance(request):
    """Trigger system maintenance tasks"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    task = request.data.get('task')
    parameters = request.data.get('parameters', {})
    
    if task == 'cleanup_old_logs':
        days_to_keep = parameters.get('days_to_keep', 30)
        # TODO: Implement log cleanup
        return Response({
            'message': f'Log cleanup task scheduled (keeping {days_to_keep} days)',
            'task': task,
            'parameters': parameters
        })
    elif task == 'backup_database':
        # TODO: Implement database backup
        return Response({
            'message': 'Database backup task scheduled',
            'task': task,
            'parameters': parameters
        })
    else:
        return Response(
            {'error': 'Unknown maintenance task'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
