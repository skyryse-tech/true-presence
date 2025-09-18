from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    users = serializers.DictField()
    attendance = serializers.DictField()
    cameras = serializers.DictField()
    face_recognition = serializers.DictField()
    system = serializers.DictField()


class SystemHealthSerializer(serializers.Serializer):
    """Serializer for system health"""
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    services = serializers.DictField()
    performance = serializers.DictField()


class MaintenanceTaskSerializer(serializers.Serializer):
    """Serializer for maintenance tasks"""
    task = serializers.CharField()
    parameters = serializers.DictField(required=False)
