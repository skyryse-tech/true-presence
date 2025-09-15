from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Camera, CameraHealthLog, CameraEvent
from .serializers import (
    CameraSerializer, CameraCreateSerializer, CameraUpdateSerializer,
    CameraHealthLogSerializer, CameraEventSerializer, CameraTestSerializer,
    CameraStreamSerializer
)


class CameraListView(generics.ListCreateAPIView):
    """List all cameras or create a new camera"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CameraCreateSerializer
        return CameraSerializer
    
    def get_queryset(self):
        return Camera.objects.filter(is_active=True).order_by('name')


class CameraDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a camera"""
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Camera.objects.all()


class CameraHealthLogListView(generics.ListAPIView):
    """List camera health logs"""
    serializer_class = CameraHealthLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        camera_id = self.kwargs.get('camera_id')
        if camera_id:
            return CameraHealthLog.objects.filter(camera_id=camera_id).order_by('-timestamp')
        return CameraHealthLog.objects.all().order_by('-timestamp')


class CameraEventListView(generics.ListAPIView):
    """List camera events"""
    serializer_class = CameraEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        camera_id = self.kwargs.get('camera_id')
        queryset = CameraEvent.objects.all()
        
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by resolved status
        is_resolved = self.request.query_params.get('is_resolved')
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        return queryset.order_by('-timestamp')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def camera_stream(request, camera_id):
    """Get camera stream URL"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    stream_url = camera.get_stream_url()
    if stream_url:
        return Response({
            'camera_id': camera_id,
            'stream_url': stream_url,
            'stream_type': camera.camera_type,
            'is_accessible': True
        })
    else:
        return Response({
            'camera_id': camera_id,
            'stream_url': None,
            'stream_type': camera.camera_type,
            'is_accessible': False,
            'error_message': 'Stream URL not configured'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_camera_connection(request, camera_id):
    """Test camera connection"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    # TODO: Implement actual camera connection test
    # For now, simulate the test
    try:
        # Simulate connection test
        import time
        time.sleep(1)  # Simulate network delay
        
        # Update camera status
        camera.status = 'online'
        camera.last_seen = timezone.now()
        camera.save()
        
        # Create health log
        CameraHealthLog.objects.create(
            camera=camera,
            status='online',
            quality_score=0.95,
            bandwidth_usage='2.3 Mbps',
            error_count=0
        )
        
        return Response({
            'camera_id': camera_id,
            'status': 'success',
            'message': 'Camera connection test successful',
            'camera_status': 'online'
        })
        
    except Exception as e:
        # Update camera status to error
        camera.status = 'error'
        camera.save()
        
        # Create health log with error
        CameraHealthLog.objects.create(
            camera=camera,
            status='error',
            error_message=str(e),
            error_count=1
        )
        
        return Response({
            'camera_id': camera_id,
            'status': 'error',
            'message': f'Camera connection test failed: {str(e)}',
            'camera_status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def camera_health(request, camera_id):
    """Get camera health status"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    # Get latest health log
    latest_health = CameraHealthLog.objects.filter(camera=camera).first()
    
    health_data = {
        'camera_id': camera_id,
        'status': camera.status,
        'uptime': str(latest_health.uptime) if latest_health and latest_health.uptime else None,
        'last_frame': latest_health.last_frame if latest_health else None,
        'quality_score': latest_health.quality_score if latest_health else 0.0,
        'bandwidth_usage': latest_health.bandwidth_usage if latest_health else None,
        'error_count': latest_health.error_count if latest_health else 0
    }
    
    return Response(health_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_camera_status(request, camera_id):
    """Update camera status"""
    camera = get_object_or_404(Camera, id=camera_id)
    
    new_status = request.data.get('status')
    if new_status not in [choice[0] for choice in Camera.STATUS_CHOICES]:
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    camera.status = new_status
    if new_status == 'online':
        camera.last_seen = timezone.now()
    camera.save()
    
    # Create health log
    CameraHealthLog.objects.create(
        camera=camera,
        status=new_status,
        quality_score=request.data.get('quality_score', 0.0),
        bandwidth_usage=request.data.get('bandwidth_usage'),
        error_count=request.data.get('error_count', 0),
        error_message=request.data.get('error_message')
    )
    
    return Response({
        'camera_id': camera_id,
        'status': new_status,
        'message': f'Camera status updated to {new_status}'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def camera_statistics(request):
    """Get camera statistics"""
    total_cameras = Camera.objects.count()
    online_cameras = Camera.objects.filter(status='online').count()
    offline_cameras = Camera.objects.filter(status='offline').count()
    error_cameras = Camera.objects.filter(status='error').count()
    
    # Get recent events
    recent_events = CameraEvent.objects.filter(
        timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
    ).count()
    
    return Response({
        'total_cameras': total_cameras,
        'online_cameras': online_cameras,
        'offline_cameras': offline_cameras,
        'error_cameras': error_cameras,
        'recent_events_24h': recent_events,
        'uptime_percentage': (online_cameras / total_cameras * 100) if total_cameras > 0 else 0
    })
