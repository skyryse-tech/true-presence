from rest_framework import serializers


class AttendanceReportSerializer(serializers.Serializer):
    """Serializer for attendance reports"""
    report_id = serializers.CharField()
    generated_at = serializers.DateTimeField()
    period = serializers.CharField()
    date_range = serializers.CharField()
    total_employees = serializers.IntegerField()
    total_attendances = serializers.IntegerField()
    unique_persons = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    department_stats = serializers.DictField()


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for real-time analytics"""
    current_occupancy = serializers.IntegerField()
    today_attendance = serializers.IntegerField()
    peak_hour = serializers.CharField()
    avg_processing_time = serializers.FloatField()
    system_health = serializers.DictField()
    camera_status = serializers.DictField()


class PatternAnalysisSerializer(serializers.Serializer):
    """Serializer for pattern analysis"""
    daily_patterns = serializers.DictField()
    seasonal_trends = serializers.DictField()
    predictions = serializers.DictField()


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for export requests"""
    format = serializers.ChoiceField(choices=['json', 'pdf', 'excel'])
    report_type = serializers.ChoiceField(choices=['attendance', 'analytics', 'patterns'])
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    department = serializers.CharField(required=False, allow_blank=True)
    employee_ids = serializers.CharField(required=False, allow_blank=True)
