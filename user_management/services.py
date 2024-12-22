from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random
import string
from .models import EmailVerificationCode

User = get_user_model()

async def get_user_name(user_id):
    user = await User.objects.aget(id=user_id)
    return user.nickname

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_verification_code(email, code):
    subject = "Email Verification"
    message = f"Your verification code is: {code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    
def expire_previous_codes(email):
    EmailVerificationCode.objects.filter(email=email, is_used=False).update(is_used=True)
    
def process_email_verification_code(email):
    expire_previous_codes(email)
    code = generate_verification_code()
    EmailVerificationCode.objects.create(email=email, code=code)
    send_verification_code(email, code)