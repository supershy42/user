from rest_framework import serializers
from config.custom_validation_error import CustomValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User
from config.error_type import ErrorType
from .services import AuthService


class NicknameCheckSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    
    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise CustomValidationError(ErrorType.NICKNAME_ALREADY_EXISTS)
        return value


class EmailCheckAndSendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise CustomValidationError(ErrorType.EMAIL_ALREADY_EXISTS)
        return value
    
    def save(self):
        email = self.validated_data['email']
        AuthService.process_email_verification_code(email)


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nickname = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        
        verification_record = AuthService.verify_email_code(email, code)

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


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'avatar']
        read_only_fields = ['id', 'email']

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        avatar_file = self.context['request'].FILES.get('avatar')
        if avatar_file:
            instance.avatar = avatar_file
        instance.save()
        return instance
        

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'is_online']