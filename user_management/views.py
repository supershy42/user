from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import (
    EmailCheckAndSendCodeSerializer,
    NicknameCheckSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    VerifyCodeSerializer,
    UserWinLossSerializer
    )
from config.response_builder import response_ok, response_error, response_errors
from .models import User
from rest_framework import status
from .services import MailService, AuthService
from config.custom_validation_error import CustomValidationError
from rest_framework.response import Response
from django.db import transaction
from config.error_type import ErrorType

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
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = AuthService.authenticate_user(email, password)
            except CustomValidationError as e:
                return response_errors(errors=e)
            if user.is_2fa_enabled:
                AuthService.process_email_verification_code(email)
                return response_ok({
                    "message": "2FA_REQUIRED",
                    "email": email
                }, status=status.HTTP_202_ACCEPTED)
            data = AuthService.generate_token_with_user(user)
            return response_ok(data)
        return response_errors(errors=serializer.errors)
    
    
class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = AuthService.verify_user_email_code(email, code)
                data = AuthService.generate_token_with_user(user)
                return response_ok(data)
            except CustomValidationError as e:
                return response_error(e)
        return response_errors(serializer.errors)


class MyProfileView(APIView):
    def get(self, request):
        user = get_object_or_404(User, id=request.user_id)
        serializer = UserProfileSerializer(user)
        return response_ok(serializer.data)

    def put(self, request):
        user = get_object_or_404(User, id=request.user_id)
        serializer = UserProfileSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return response_ok(serializer.data)
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
        
        
class SearchUserView(APIView):
    def get(self, request):
        nickname = request.query_params.get('nickname')
        if not nickname:
            return Response({"message":"nickname param required."}, status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return Response({"messsage":"user not found."}, status.HTTP_404_NOT_FOUND)
        
        data = UserProfileSerializer(user).data
        return response_ok(data)


class UpdateUserWinLossView(APIView):
    @transaction.atomic
    def put(self, request, user_id):
        if user_id != request.user_id:
            return response_error(ErrorType.PERMISSION_DENIED)

        try:
            user = User.objects.select_for_update().get(id=user_id)
        except User.DoesNotExist:
            return response_error(ErrorType.USER_NOT_FOUND)
            
        serializer = UserWinLossSerializer(instance=user, data=request.data)
        if not serializer.is_valid():
            return response_errors(serializer.errors)

        serializer.save()
        return response_ok({
            "wins": user.wins,
            "losses": user.losses
        })