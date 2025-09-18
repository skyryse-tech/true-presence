from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid
import json
from .models import FaceTemplate, FaceEnrollmentTask, FaceVerificationTask, FaceVerificationResult
from .serializers import (
    FaceEnrollmentSerializer, FaceEnrollmentTaskSerializer,
    FaceVerificationSerializer, FaceVerificationTaskSerializer,
    FaceVerificationResultSerializer, BulkVerificationSerializer,
    FaceTemplateSerializer
)

User = get_user_model()


class FaceEnrollmentView(generics.CreateAPIView):
    """Face enrollment endpoint"""
    serializer_class = FaceEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee_id = serializer.validated_data['employee_id']
        images = serializer.validated_data['images']
        quality_check = serializer.validated_data.get('quality_check', True)
        
        try:
            user = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create enrollment task
        task = FaceEnrollmentTask.objects.create(
            user=user,
            images=images,
            status='queued'
        )
        
        # TODO: Queue task for AI processing
        # For now, simulate immediate processing
        self.process_enrollment_task(task, quality_check)
        
        response_serializer = FaceEnrollmentTaskSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def process_enrollment_task(self, task, quality_check):
        """Process enrollment task (placeholder for AI service integration)"""
        try:
            task.status = 'processing'
            task.save()
            
            # Simulate processing
            import time
            time.sleep(1)  # Simulate processing time
            
            # Create face template (placeholder)
            face_template = FaceTemplate.objects.create(
                user=task.user,
                template_data=b'placeholder_template_data',
                quality_score=0.95,
                enrollment_images=task.images[:3]  # Store first 3 images
            )
            
            # Update user
            task.user.face_enrolled = True
            task.user.enrollment_date = timezone.now()
            task.user.save()
            
            # Complete task
            task.status = 'completed'
            task.result = {
                'success': True,
                'faces_detected': len(task.images),
                'quality_scores': [0.92, 0.89, 0.94],
                'template_created': True,
                'message': 'Face template created successfully'
            }
            task.processing_time = 1.0
            task.completed_at = timezone.now()
            task.save()
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()


class FaceEnrollmentStatusView(generics.RetrieveAPIView):
    """Get enrollment task status"""
    serializer_class = FaceEnrollmentTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return FaceEnrollmentTask.objects.all()


class FaceVerificationView(generics.CreateAPIView):
    """Face verification endpoint"""
    serializer_class = FaceVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image = serializer.validated_data['image']
        camera_id = serializer.validated_data.get('camera_id')
        location = serializer.validated_data.get('location')
        
        # Create verification task
        task = FaceVerificationTask.objects.create(
            image=image,
            camera_id=camera_id,
            location=location,
            status='queued'
        )
        
        # TODO: Queue task for AI processing
        # For now, simulate immediate processing
        self.process_verification_task(task)
        
        response_serializer = FaceVerificationTaskSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def process_verification_task(self, task):
        """Process verification task (placeholder for AI service integration)"""
        try:
            task.status = 'processing'
            task.save()
            
            # Simulate processing
            import time
            time.sleep(0.5)  # Simulate processing time
            
            # Simulate recognition result
            # In real implementation, this would call the AI service
            recognized = True  # Simulate successful recognition
            confidence = 0.97
            user = User.objects.first()  # Simulate finding a user
            
            if recognized and user:
                # Create verification result
                result = FaceVerificationResult.objects.create(
                    task=task,
                    user=user,
                    recognized=True,
                    confidence=confidence,
                    similarity_score=0.92,
                    is_live=True,
                    anti_spoof_score=0.98,
                    face_quality=0.95,
                    face_position={'x': 100, 'y': 100, 'width': 200, 'height': 200}
                )
                
                task.result = {
                    'recognized': True,
                    'employee_id': user.employee_id,
                    'name': user.get_full_name(),
                    'confidence': confidence,
                    'similarity_score': 0.92,
                    'is_live': True,
                    'anti_spoof_score': 0.98,
                    'attendance_logged': True,
                    'timestamp': timezone.now().isoformat()
                }
            else:
                task.result = {
                    'recognized': False,
                    'confidence': 0.0,
                    'message': 'No matching face found'
                }
            
            # Complete task
            task.status = 'completed'
            task.processing_time = 0.5
            task.completed_at = timezone.now()
            task.save()
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()


class FaceVerificationStatusView(generics.RetrieveAPIView):
    """Get verification task status"""
    serializer_class = FaceVerificationTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return FaceVerificationTask.objects.all()


class BulkVerificationView(generics.CreateAPIView):
    """Bulk face verification endpoint"""
    serializer_class = BulkVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        images = serializer.validated_data['images']
        options = serializer.validated_data.get('options', {})
        
        # Process each image
        results = []
        for img_data in images:
            task = FaceVerificationTask.objects.create(
                image=img_data['image'],
                camera_id=img_data.get('id'),
                status='queued'
            )
            
            # Simulate processing
            self.process_verification_task(task)
            
            results.append({
                'id': img_data.get('id'),
                'task_id': str(task.id),
                'result': task.result
            })
        
        return Response({'results': results}, status=status.HTTP_200_OK)


class FaceTemplateListView(generics.ListAPIView):
    """List all face templates"""
    serializer_class = FaceTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FaceTemplate.objects.filter(is_active=True)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def enrollment_status(request, task_id):
    """Get enrollment task status by ID"""
    try:
        task = FaceEnrollmentTask.objects.get(id=task_id)
        serializer = FaceEnrollmentTaskSerializer(task)
        return Response(serializer.data)
    except FaceEnrollmentTask.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verification_status(request, task_id):
    """Get verification task status by ID"""
    try:
        task = FaceVerificationTask.objects.get(id=task_id)
        serializer = FaceVerificationTaskSerializer(task)
        return Response(serializer.data)
    except FaceVerificationTask.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
