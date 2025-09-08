# from rest_framework import serializers
# from .models import Employee

# class EmployeeSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Employee model.
#     """
#     class Meta:
#         model = Employee
#         fields = ['employee_id', 'first_name', 'last_name', 'email', 'is_active', 'created_at']
#         read_only_fields = ['created_at']

# class EnrollmentSerializer(serializers.Serializer):
#     """
#     Serializer for the enrollment request. Requires an employee_id and a base64-encoded image.
#     """
#     employee_id = serializers.CharField(max_length=100)
#     image = serializers.CharField() # Base64 encoded image string

#     def validate_employee_id(self, value):
#         """Check that the employee exists."""
#         if not Employee.objects.filter(employee_id=value).exists():
#             raise serializers.ValidationError("Employee with this ID does not exist.")
#         return value

# class VerificationSerializer(serializers.Serializer):
#     """
#     Serializer for the verification request. Requires just a base64-encoded image.
#     """
#     image = serializers.CharField() # Base64 encoded image string
from rest_framework import serializers
from .models import Employee, AttendanceLog

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class EnrollmentSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    image = serializers.CharField()  # base64

class VerificationSerializer(serializers.Serializer):
    image = serializers.CharField()  # base64

class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = '__all__'