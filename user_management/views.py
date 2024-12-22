from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import (
    EmailCheckAndSendCodeSerializer,
    NicknameCheckSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer
    )
from config.response_builder import response_ok, response_error, response_errors
from .models import User
from rest_framework import status
from .services import MailService
from config.custom_validation_error import CustomValidationError

class NicknameCheckView(APIView):
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        if serializer.is_valid():
            return response_ok()
        return response_errors(errors=serializer.errors)


class EmailCheckAndSendCodeView(APIView):
    def post(self, request):
        serializer = EmailCheckAndSendCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response_ok(message="Verification code sent")
        return response_errors(errors=serializer.errors)


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response_ok(status=status.HTTP_201_CREATED)
        return response_errors(errors=serializer.errors)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            auth_data = serializer.save()
            return response_ok(auth_data)
        return response_errors(errors=serializer.errors)


class UserProfileView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserProfileSerializer(user)
        return response_ok(serializer.data)
    

class SendEmailView(APIView):
    def post(self, request):
        try:
            MailService.validate_email_request(request)
        except CustomValidationError as e:
            return response_error(e)
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')
        MailService.custom_send_email(email, subject, message)
        return response_ok()
        