from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import 
from . import services
from .serializers import UserRegistrationSerializer, EmailVerificationSerializer, UserLoginSerializer, UserProfileSerializer, EmailVerifyRequestSerializer
from django.shortcuts import get_object_or_404
from .models import User

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. Please check your email for the verification code."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class EmailVerifyRequestView(APIView):
    def post(self, request):
        serializer = EmailVerifyRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            services.request_verification_code(email)
            return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class EmailVerificationView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verification successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            auth_data = serializer.save()
            return Response(auth_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    def get(self, request, user_id):
        user = 
        
        
        (User, id=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)