# from django.db import models
# from pgvector.django import VectorField

# class Employee(models.Model):
#     """
#     Represents an employee with their personal details and face embedding.
#     """
#     employee_id = models.CharField(max_length=100, unique=True, primary_key=True)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     # pgvector field to store the 512-dimension ArcFace embedding
#     face_embedding = VectorField(dimensions=512, null=True, blank=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.employee_id})"

# class AttendanceLog(models.Model):
#     """
#     Logs a record each time an employee is successfully verified.
#     """
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_logs')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     notes = models.TextField(blank=True, null=True) # Optional field for any notes

#     def __str__(self):
#         return f"Log for {self.employee.first_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
from django.db import models
from pgvector.django import VectorField

class Employee(models.Model):
    employee_id = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    face_embedding = VectorField(dimensions=512, null=True)  # ArcFace embedding

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)