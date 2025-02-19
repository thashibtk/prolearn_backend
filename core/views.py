from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import CustomUser, OTP
from rest_framework.permissions import IsAuthenticated
from .serializers import SignupSerializer, LoginSerializer, OTPSerializer, UserSerializer
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
    



# import json
# from django.contrib.auth import get_user_model
# from rest_framework.response import Response
# from rest_framework import status, generics
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import AllowAny
# from .serializers import UserSerializer, LoginSerializer
# from django.http import JsonResponse
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated

# from django.shortcuts import get_object_or_404
# from django.core.mail import send_mail
# from .models import OTP
# import random
# from django.views.decorators.csrf import csrf_exempt
# import logging

# logger = logging.getLogger(__name__)


# User = get_user_model()

# def api_root(request):
#     return JsonResponse({"message": "Welcome to the Auth API!", "endpoints": ["/register/", "/login/", "/logout/"]})

# class ProtectedView(APIView):
#     permission_classes = [IsAuthenticated]  # Requires Authentication

#     def get(self, request):
#         return Response({"message": "You are authenticated!"})
    

# class UserDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         return Response({
#             "id": user.id,
#             # "username": user.username,
#             "email": user.email
#         })


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         print("Received Data:", request.data)
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             return super().create(request, *args, **kwargs)
#         else:
#             print("Serializer Errors:", serializer.errors)
#             return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



# @csrf_exempt
# def send_otp(request):
#     try:
#         logger.info(f"Received request body: {request.body}")

#         if request.method == "POST":
#             try:
#                 data = json.loads(request.body)
#                 email = data.get("email")
#                 logger.info(f"Email received: {email}")
#             except json.JSONDecodeError:
#                 logger.error("Invalid JSON format")
#                 return JsonResponse({"error": "Invalid JSON format"}, status=400)

#             if not email:
#                 logger.error("Email is missing")
#                 return JsonResponse({"error": "Email is required"}, status=400)

#             otp = random.randint(100000, 999999)  # Generate OTP
#             OTP.objects.create(email=email, otp_code=otp)

#             send_mail(
#                 "Your OTP Code",
#                 f"Your OTP code is {otp}.",
#                 "pocker0272@gmail.com",  # ✅ Ensure this matches EMAIL_HOST_USER
#                 [email],
#                 fail_silently=False,
#             )

#             logger.info(f"OTP sent to {email}")
#             return JsonResponse({"message": "OTP sent successfully!"})

#         return JsonResponse({"error": "Invalid request method"}, status=400)

#     except Exception as e:
#         logger.error(f"Error occurred: {str(e)}")
#         return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

# @csrf_exempt  # Add this
# def verify_otp(request):
#     """Verify OTP entered by user."""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get("email")
#             otp_code = data.get("otp_code")

#             if not email or not otp_code:
#                 return JsonResponse({"error": "Email and OTP code are required."}, status=400)

#             # Use filter to get all OTPs for the email
#             otp = OTP.objects.filter(email=email).order_by('-created_at').first()

#             if not otp:
#                 return JsonResponse({"error": "OTP not found for this email."}, status=400)

#             # Check if OTP has expired
#             if otp.is_expired():
#                 return JsonResponse({"error": "OTP has expired"}, status=400)

#             if otp.otp_code == otp_code:
#                 otp.delete()  # Remove OTP after successful verification
#                 return JsonResponse({"message": "OTP verified successfully"}, status=200)
#             else:
#                 return JsonResponse({"error": "Invalid OTP"}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)

#     return JsonResponse({"error": "Invalid request method"}, status=400)


# class LoginView(generics.GenericAPIView):
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         print("Received Login Data:", request.data)  # ✅ Log input
#         serializer = self.get_serializer(data=request.data)

#         if not serializer.is_valid():
#             print("Serializer Errors:", serializer.errors)  # ✅ Log validation errors
#             return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#         user = serializer.validated_data  # ✅ Should be a User object
#         print("Authenticated User:", user)

#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#         })

# class LogoutView(generics.GenericAPIView):
#     def post(self, request):
#         try:
#             token = request.data.get("refresh")
#             RefreshToken(token).blacklist()
#             return Response({"message": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
#         except:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# class DashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({"message": "Welcome to the dashboard!"})
