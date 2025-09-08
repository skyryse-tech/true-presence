from rest_framework import status, views
from rest_framework.response import Response
from .serializers import EmployeeSerializer, EnrollmentSerializer, VerificationSerializer
from .models import Employee
import pika
import os
import json
import uuid
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- SERVICE CONNECTIONS ---
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def publish_to_rabbitmq(task_body):
    """Helper function to publish a task to the RabbitMQ queue."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=json.dumps(task_body),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        connection.close()
        return True
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return False


class EnrollView(views.APIView):
    """
    API endpoint for enrolling an employee's face.
    Accepts a POST request with 'employee_id' and a base64 'image'.
    """
    def post(self, request, *args, **kwargs):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            task_id = f"enroll_{uuid.uuid4()}"
            
            task = {
                'task_id': task_id,
                'type': 'enroll',
                'employee_id': data['employee_id'],
                'image': data['image']
            }

            if publish_to_rabbitmq(task):
                return Response({'task_id': task_id, 'status': 'Task queued for enrollment.'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error': 'Could not connect to the processing queue.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyView(views.APIView):
    """
    API endpoint for verifying a face for attendance.
    Accepts a POST request with a base64 'image'.
    """
    def post(self, request, *args, **kwargs):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            task_id = f"verify_{uuid.uuid4()}"
            
            task = {
                'task_id': task_id,
                'type': 'verify',
                'image': data['image']
            }
            
            if publish_to_rabbitmq(task):
                return Response({'task_id': task_id, 'status': 'Task queued for verification.'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error': 'Could not connect to the processing queue.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskResultView(views.APIView):
    """
    API endpoint to check the result of an enrollment or verification task.
    """
    def get(self, request, task_id, *args, **kwargs):
        result_json = redis_client.get(task_id)
        
        if result_json:
            result = json.loads(result_json)
            # Optionally remove the key from Redis after fetching
            # redis_client.delete(task_id)
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'pending', 'message': 'Task is still being processed or does not exist.'}, status=status.HTTP_202_ACCEPTED)

# You would also create standard CRUD views for managing Employees
# For simplicity, we are focusing on the core attendance logic here.
