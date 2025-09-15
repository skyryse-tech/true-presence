from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer, RegisterSerializer, ChangePasswordSerializer, ResetPasswordSerializer

User = get_user_model()


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'employee_id': user.employee_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'department': user.department,
                    'face_enrolled': user.face_enrolled,
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(generics.GenericAPIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'employee_id': user.employee_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'department': user.department,
            }
        }, status=status.HTTP_201_CREATED)


class ChangePasswordView(generics.GenericAPIView):
    """Change password endpoint"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'error': e.messages}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})


class ResetPasswordView(generics.GenericAPIView):
    """Reset password request endpoint"""
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            # TODO: Send password reset email
            # For now, just return success
            return Response({
                'message': 'Password reset email sent successfully'
            })
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({
                'message': 'If the email exists, a password reset link has been sent'
            })


class ResetPasswordConfirmView(generics.GenericAPIView):
    """Reset password confirmation endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        # TODO: Implement password reset confirmation
        # This would typically involve token validation
        return Response({
            'message': 'Password reset confirmation endpoint - to be implemented'
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'employee_id': user.employee_id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'department': user.department,
        'phone_number': user.phone_number,
        'face_enrolled': user.face_enrolled,
        'enrollment_date': user.enrollment_date,
        'last_attendance': user.last_attendance,
        'is_active': user.is_active,
        'created_at': user.created_at,
        'last_login': user.last_login,
    })