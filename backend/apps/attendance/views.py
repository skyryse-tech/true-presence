from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, date, timedelta
from .models import AttendanceLog, AttendanceSummary, AttendanceRule
from .serializers import (
    AttendanceLogSerializer, AttendanceLogCreateSerializer,
    AttendanceSummarySerializer, AttendanceRuleSerializer,
    AttendanceStatsSerializer, ManualAttendanceSerializer
)

User = get_user_model()


class AttendanceLogListView(generics.ListAPIView):
    """List attendance logs with filtering"""
    serializer_class = AttendanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AttendanceLog.objects.select_related('user').all()
        
        # Filter by employee_id
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(user__employee_id=employee_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        
        # Filter by camera
        camera_id = self.request.query_params.get('camera_id')
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(user__department__icontains=department)
        
        return queryset.order_by('-timestamp')


class AttendanceLogCreateView(generics.CreateAPIView):
    """Create new attendance log"""
    serializer_class = AttendanceLogCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AttendanceSummaryView(generics.ListAPIView):
    """Get attendance summary statistics"""
    serializer_class = AttendanceSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AttendanceSummary.objects.select_related('user').all()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset.order_by('-date')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_stats(request):
    """Get attendance statistics"""
    period = request.query_params.get('period', 'daily')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    department = request.query_params.get('department')
    
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
    
    # Calculate statistics
    total_attendances = queryset.count()
    unique_persons = queryset.values('user').distinct().count()
    
    # Department statistics
    dept_stats = {}
    if not department:
        dept_data = queryset.values('user__department').annotate(
            count=Count('id')
        ).order_by('-count')
        dept_stats = {item['user__department'] or 'Unknown': item['count'] 
                     for item in dept_data}
    
    # Hourly distribution
    hourly_data = queryset.extra(
        select={'hour': 'EXTRACT(hour FROM timestamp)'}
    ).values('hour').annotate(count=Count('id')).order_by('hour')
    hourly_distribution = {f"{item['hour']:02d}:00": item['count'] 
                          for item in hourly_data}
    
    stats_data = {
        'period': period,
        'date': date_to,
        'total_attendances': total_attendances,
        'unique_persons': unique_persons,
        'departments': dept_stats,
        'hourly_distribution': hourly_distribution
    }
    
    serializer = AttendanceStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_manual_attendance(request):
    """Mark manual attendance (Admin only)"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ManualAttendanceSerializer(data=request.data)
    if serializer.is_valid():
        employee_id = serializer.validated_data['employee_id']
        timestamp = serializer.validated_data['timestamp']
        reason = serializer.validated_data['reason']
        
        try:
            user = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create attendance log
        attendance_log = AttendanceLog.objects.create(
            user=user,
            timestamp=timestamp,
            attendance_type='check_in',
            notes=f"Manual entry: {reason}",
            confidence=1.0  # Manual entry has 100% confidence
        )
        
        # Update user's last attendance
        user.last_attendance = timestamp
        user.save()
        
        response_serializer = AttendanceLogSerializer(attendance_log)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceRuleListView(generics.ListCreateAPIView):
    """List and create attendance rules"""
    serializer_class = AttendanceRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AttendanceRule.objects.filter(is_active=True).order_by('-created_at')


class AttendanceRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete attendance rule"""
    serializer_class = AttendanceRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AttendanceRule.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_attendance_history(request, employee_id):
    """Get attendance history for a specific user"""
    try:
        user = User.objects.get(employee_id=employee_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get date range
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    queryset = user.attendance_logs.all()
    
    if date_from:
        queryset = queryset.filter(timestamp__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(timestamp__date__lte=date_to)
    
    serializer = AttendanceLogSerializer(queryset.order_by('-timestamp'), many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def today_attendance(request):
    """Get today's attendance records"""
    today = date.today()
    queryset = AttendanceLog.objects.filter(
        timestamp__date=today
    ).select_related('user').order_by('-timestamp')
    
    serializer = AttendanceLogSerializer(queryset, many=True)
    return Response(serializer.data)