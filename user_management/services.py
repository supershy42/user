from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random
import string
from .models import EmailVerificationCode
from config.custom_validation_error import CustomValidationError
from config.error_type import ErrorType
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserService:
    @staticmethod
    async def get_user_name(user_id):
        user = await User.objects.aget(id=user_id)
        return user.nickname
    
    
class AuthService:
    @staticmethod
    def generate_verification_code(length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    @staticmethod
    def expire_previous_codes(email):
        EmailVerificationCode.objects.filter(email=email, is_used=False).update(is_used=True)
        
    @staticmethod
    def send_verification_code(email, code):
        subject = "Email Verification"
        message = f"Your verification code is: {code}"
        MailService.custom_send_email(email, subject, message)
        
    @staticmethod
    def process_email_verification_code(email):
        AuthService.expire_previous_codes(email)
        code = AuthService.generate_verification_code()
        EmailVerificationCode.objects.create(email=email, code=code)
        AuthService.send_verification_code(email, code)
    
    @staticmethod
    def authenticate_user(email, password) -> User:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorType.INVALID_CREDENTIALS)

        if not user.check_password(password):
            raise CustomValidationError(ErrorType.INVALID_CREDENTIALS)
        
        return user
    
    @staticmethod
    def generate_token_with_user(user):
        jwt = AuthService.generate_jwt_tokens(user)
        from .serializers import UserProfileSerializer
        user_detail = UserProfileSerializer(user).data
        
        return {
            **jwt,
            **user_detail
        }
    
    @staticmethod
    def generate_jwt_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    @staticmethod
    def verify_user_email_code(email, code):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorType.USER_ID_NOT_FOUND)
        AuthService.verify_email_code(email, code)
        return user
        
    @staticmethod
    def verify_email_code(email, code):
        try:
            verification_record = EmailVerificationCode.objects.filter(email=email, code=code, is_used=False).latest('created_at')
        except EmailVerificationCode.DoesNotExist:
            raise CustomValidationError(ErrorType.INVALID_VERIFICATION_CODE)
        if verification_record.is_expired:
            raise CustomValidationError(ErrorType.VERIFICATION_CODE_EXPIRED)
        
        return verification_record


class MailService:
    @staticmethod
    def custom_send_email(email, subject, message):
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        
    @staticmethod
    def validate_email_request(request):
        if not request.data.get('email'):
            raise CustomValidationError(ErrorType.INVALID_EMAIL_REQUEST)
        if not request.data.get('subject'):
            raise CustomValidationError(ErrorType.EMAIL_ALREADY_EXISTS)
        if not request.data.get('message'):
            raise CustomValidationError(ErrorType.INVALID_VERIFICATION_CODE)
