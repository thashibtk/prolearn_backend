from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, OTP
import random

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role', 'is_active']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return {'user': user}

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['email', 'otp_code']

    def validate(self, data):
        try:
            otp_instance = OTP.objects.filter(email=data['email']).latest('created_at')
            if otp_instance.is_expired():
                raise serializers.ValidationError("OTP has expired")
            if otp_instance.otp_code != data['otp_code']:
                raise serializers.ValidationError("Invalid OTP")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("OTP not found")
        return data


class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_role(self, value):
        if value not in ['project_manager', 'mentor']:
            raise serializers.ValidationError("Only 'team_lead' or 'mentor' can be created by Admins.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )
        user.role = validated_data['role']
        user.save()
        return user
