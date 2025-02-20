from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from .models import CustomUser, OTP
from rest_framework.permissions import IsAuthenticated
from .serializers import SignupSerializer, LoginSerializer, OTPSerializer, UserSerializer,AdminCreateUserSerializer
import random

# Generate JWT Token
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Signup View
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            return Response({"tokens": tokens, "user": UserSerializer(user).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OTP Send View
class OTPSendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(email=email, otp_code=otp_code)

        send_mail(
            "Your OTP Code",
            f"Your OTP code is {otp_code}. It will expire in 10 minutes.",
            "noreply@prolearn.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

# OTP Verify View
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Welcome to the Dashboard!", "user": request.user.email}, status=200)
    
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny

class AdminLoginView(APIView):
    permission_classes = [AllowAny]  # This makes the endpoint public

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate user
        user = authenticate(email=email, password=password)

        if user is None or user.role != "admin":
            return Response({"error": "Invalid Admin Credentials"}, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    if request.user.role != 'admin':
        return Response({"error": "Only Admins can create users"}, status=status.HTTP_403_FORBIDDEN)

    serializer = AdminCreateUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": f"User {serializer.validated_data['role']} created successfully"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    if request.user.role != 'admin':
        return Response({"error": "Only Admins can view users"}, status=status.HTTP_403_FORBIDDEN)

    # Filter to include only mentors and project managers
    users = CustomUser.objects.filter(role__in=["mentor", "project_manager"])  

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return Response({"error": "Only Admins can delete users"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_user_status(request, user_id):
    if request.user.role != 'admin':
        return Response({"error": "Only Admins can freeze/unfreeze users"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active  # Toggle active status
        user.save()
        status_text = "frozen" if not user.is_active else "unfrozen"
        return Response({"message": f"User {status_text} successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_freeze_user(request, user_id):
    if not request.user.is_staff:  # Ensure only admins can toggle freeze
        return Response({"error": "Only admins can modify users"}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active 
        user.save()
        return Response({"message": f"User {'frozen' if not user.is_active else 'unfrozen'} successfully"})
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    
class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            return Response({"message": "Admin logged out successfully."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
            
class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff: 
            return Response({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": "admin"
            })
        return Response({"error": "Not an admin"}, status=403)
    
class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        # Ensure only admins can update users
        if request.user.role != 'admin':
            return Response({"error": "Only Admins can update users"}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(CustomUser, id=user_id)  # Get user by ID
        serializer = UserSerializer(user, data=request.data, partial=True)  # Allow partial updates

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
