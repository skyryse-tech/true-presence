from rest_framework import serializers
from .models import Camera, CameraHealthLog, CameraEvent


class CameraSerializer(serializers.ModelSerializer):
    """Serializer for Camera model"""
    stream_url = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = Camera
        fields = ['id', 'name', 'location', 'camera_type', 'ip_address', 'rtsp_url',
                 'username', 'port', 'resolution', 'fps', 'status', 'is_active',
                 'last_seen', 'created_at', 'updated_at', 'stream_url', 'is_online']
        read_only_fields = ['created_at', 'updated_at', 'last_seen']
    
    def get_stream_url(self, obj):
        return obj.get_stream_url()
    
    def get_is_online(self, obj):
        return obj.is_online()


class CameraCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cameras"""
    
    class Meta:
        model = Camera
        fields = ['id', 'name', 'location', 'camera_type', 'ip_address', 'rtsp_url',
                 'username', 'password', 'port', 'resolution', 'fps', 'is_active']
    
    def create(self, validated_data):
        # Set initial status to offline
        validated_data['status'] = 'offline'
        return super().create(validated_data)


class CameraUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cameras"""
    
    class Meta:
        model = Camera
        fields = ['name', 'location', 'camera_type', 'ip_address', 'rtsp_url',
                 'username', 'password', 'port', 'resolution', 'fps', 'is_active']


class CameraHealthLogSerializer(serializers.ModelSerializer):
    """Serializer for camera health logs"""
    camera = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = CameraHealthLog
        fields = ['camera', 'status', 'uptime', 'last_frame', 'quality_score',
                 'bandwidth_usage', 'error_count', 'error_message', 'timestamp']
        read_only_fields = ['timestamp']


class CameraEventSerializer(serializers.ModelSerializer):
    """Serializer for camera events"""
    camera = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = CameraEvent
        fields = ['id', 'camera', 'event_type', 'severity', 'message', 'metadata',
                 'timestamp', 'is_resolved', 'resolved_at']
        read_only_fields = ['id', 'timestamp', 'resolved_at']


class CameraTestSerializer(serializers.Serializer):
    """Serializer for testing camera connection"""
    camera_id = serializers.CharField(max_length=50)
    
    def validate_camera_id(self, value):
        try:
            Camera.objects.get(id=value)
        except Camera.DoesNotExist:
            raise serializers.ValidationError("Camera not found")
        return value


class CameraStreamSerializer(serializers.Serializer):
    """Serializer for camera stream information"""
    stream_url = serializers.URLField()
    stream_type = serializers.CharField()
    is_accessible = serializers.BooleanField()
    error_message = serializers.CharField(required=False, allow_blank=True)
