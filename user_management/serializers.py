from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from config.custom_validation_error import CustomValidationError
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from .models import User, EmailVerificationCode
from .services import process_email_verification_code
from config.error_type import ErrorType


class NicknameCheckSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    
    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise CustomValidationError(ErrorType.CONFLICT_NICKNAME)
        return value


class EmailCheckAndSendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
    def save(self):
        email = self.validated_data['email']
        process_email_verification_code(email)


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nickname = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        
        try:
            verification_record = EmailVerificationCode.objects.get(email=email, code=code)
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError({"message": "Invalid or expired verification code."})
        if verification_record.is_expired:
            raise serializers.ValidationError({"code": "The verification code has expired."})

        attrs['verification_record'] = verification_record
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password']
        )
        
        verification_record = self.validated_data['verification_record']
        verification_record.is_used = True
        verification_record.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid credentials.")

        attrs['user'] = user
        return attrs


    def save(self, **kwargs):
        user = self.validated_data['user']

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'nickname', 'avatar']


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'is_online']