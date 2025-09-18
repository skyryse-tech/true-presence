from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FaceTemplate, FaceEnrollmentTask, FaceVerificationTask, FaceVerificationResult

User = get_user_model()


class FaceEnrollmentSerializer(serializers.Serializer):
    """Serializer for face enrollment request"""
    employee_id = serializers.CharField(max_length=20)
    images = serializers.ListField(
        child=serializers.CharField(),
        min_length=3,
        max_length=3,
        help_text="List of 3 base64 encoded images (left, right, front)"
    )
    quality_check = serializers.BooleanField(default=True)


class FaceEnrollmentTaskSerializer(serializers.ModelSerializer):
    """Serializer for face enrollment task"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = FaceEnrollmentTask
        fields = ['id', 'user', 'status', 'result', 'error_message', 
                 'processing_time', 'created_at', 'completed_at']
        read_only_fields = ['id', 'user', 'status', 'result', 'error_message', 
                           'processing_time', 'created_at', 'completed_at']


class FaceVerificationSerializer(serializers.Serializer):
    """Serializer for face verification request"""
    image = serializers.CharField(help_text="Base64 encoded image")
    camera_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)


class FaceVerificationTaskSerializer(serializers.ModelSerializer):
    """Serializer for face verification task"""
    
    class Meta:
        model = FaceVerificationTask
        fields = ['id', 'camera_id', 'location', 'status', 'result', 
                 'error_message', 'processing_time', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'result', 'error_message', 
                           'processing_time', 'created_at', 'completed_at']


class FaceVerificationResultSerializer(serializers.ModelSerializer):
    """Serializer for face verification result"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = FaceVerificationResult
        fields = ['user', 'recognized', 'confidence', 'similarity_score', 
                 'is_live', 'anti_spoof_score', 'face_quality', 'face_position', 'created_at']
        read_only_fields = ['user', 'recognized', 'confidence', 'similarity_score', 
                           'is_live', 'anti_spoof_score', 'face_quality', 'face_position', 'created_at']


class BulkVerificationSerializer(serializers.Serializer):
    """Serializer for bulk face verification"""
    images = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            help_text="Dictionary with 'id' and 'image' keys"
        )
    )
    options = serializers.DictField(
        child=serializers.FloatField(),
        required=False,
        help_text="Options like max_faces, quality_threshold, similarity_threshold"
    )


class FaceTemplateSerializer(serializers.ModelSerializer):
    """Serializer for face template"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = FaceTemplate
        fields = ['id', 'user', 'quality_score', 'enrollment_images', 
                 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'user', 'quality_score', 'enrollment_images', 
                           'created_at', 'updated_at', 'is_active']
