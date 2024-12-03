from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from .models import User, EmailVerificationCode
from .services import register_user, process_email_verification_code


class UserRegistrationSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def create(self, validated_data):
        user = register_user(
            nickname=validated_data['nickname'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("This nickname is already taken.")
        return value


class SendEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "This email is not registered."})
        
        if user.is_active:
            raise serializers.ValidationError({"email": "This account is arleady active."})
        
        return attrs
    
    def save(self):
        email = self.validated_data['email']
        process_email_verification_code(email)


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        try:
            user = User.objects.get(email=email)
            verification_record = EmailVerificationCode.objects.get(email=email, code=code, is_used=False)
        except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
            raise serializers.ValidationError("Invalid verification code or email.")

        if verification_record.is_expired:
            raise serializers.ValidationError("The verification code has expired.")

        attrs['user'] = user
        attrs['verification_record'] = verification_record
        return attrs

    def save(self):
        user = self.validated_data['user']
        verification_record = self.validated_data['verification_record']
        user.is_active = True
        user.save()
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
            'is_active': user.is_active,
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'nickname', 'avatar']


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'is_online']