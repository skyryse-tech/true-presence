from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AttendanceLog, AttendanceSummary, AttendanceRule

User = get_user_model()


class AttendanceLogSerializer(serializers.ModelSerializer):
    """Serializer for attendance logs"""
    user = serializers.StringRelatedField(read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceLog
        fields = ['id', 'user', 'user_name', 'timestamp', 'attendance_type', 
                 'camera_id', 'location', 'confidence', 'verification_time', 
                 'face_position', 'photo_path', 'notes']
        read_only_fields = ['id', 'user', 'timestamp']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()


class AttendanceLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance logs"""
    
    class Meta:
        model = AttendanceLog
        fields = ['attendance_type', 'camera_id', 'location', 'confidence', 
                 'verification_time', 'face_position', 'photo_path', 'notes']


class AttendanceSummarySerializer(serializers.ModelSerializer):
    """Serializer for attendance summaries"""
    user = serializers.StringRelatedField(read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSummary
        fields = ['id', 'user', 'user_name', 'date', 'check_in_time', 'check_out_time',
                 'total_hours', 'break_duration', 'is_present', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()


class AttendanceRuleSerializer(serializers.ModelSerializer):
    """Serializer for attendance rules"""
    
    class Meta:
        model = AttendanceRule
        fields = ['id', 'name', 'description', 'check_in_time', 'check_out_time',
                 'break_duration', 'late_tolerance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    total_attendances = serializers.IntegerField()
    unique_persons = serializers.IntegerField()
    departments = serializers.DictField()
    hourly_distribution = serializers.DictField()
    period = serializers.CharField()
    date = serializers.DateField()


class ManualAttendanceSerializer(serializers.Serializer):
    """Serializer for manual attendance marking"""
    employee_id = serializers.CharField(max_length=20)
    timestamp = serializers.DateTimeField()
    reason = serializers.CharField(max_length=500)
    marked_by = serializers.EmailField()