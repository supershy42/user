from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random
import string
from .models import EmailVerificationCode
from config.custom_validation_error import CustomValidationError
from config.error_type import ErrorType

User = get_user_model()

class UserService:
    @staticmethod
    async def get_user_name(user_id):
        user = await User.objects.aget(id=user_id)
        return user.nickname


class MailService:
    @staticmethod
    def generate_verification_code(length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def send_verification_code(email, code):
        subject = "Email Verification"
        message = f"Your verification code is: {code}"
        MailService.custom_send_email(email, subject, message)

    @staticmethod
    def custom_send_email(email, subject, message):
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        
    @staticmethod
    def expire_previous_codes(email):
        EmailVerificationCode.objects.filter(email=email, is_used=False).update(is_used=True)
        
    @staticmethod
    def process_email_verification_code(email):
        MailService.expire_previous_codes(email)
        code = MailService.generate_verification_code()
        EmailVerificationCode.objects.create(email=email, code=code)
        MailService.send_verification_code(email, code)
        
    @staticmethod
    def validate_email_request(request):
        if not request.data.get('email'):
            raise CustomValidationError(ErrorType.INVALID_EMAIL_REQUEST)
        if not request.data.get('subject'):
            raise CustomValidationError(ErrorType.EMAIL_ALREADY_EXISTS)
        if not request.data.get('message'):
            raise CustomValidationError(ErrorType.INVALID_VERIFICATION_CODE)
