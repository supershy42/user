from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random
import string
from .models import EmailVerificationCode

User = get_user_model()

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def register_user(nickname, email, password):
    user = User.objects.create_user(
        nickname=nickname,
        email=email,
        password=password,
        is_active=False
    )
    
    code = generate_verification_code()
    EmailVerificationCode.objects.create(user=user, code=code)
    send_verification_email(email, code)
    return user

def send_verification_email(email, code):
    subject = "Email Verification"
    message = f"Your verification code is: {code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)