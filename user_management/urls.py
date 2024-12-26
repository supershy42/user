from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    EmailCheckAndSendCodeView,
    NicknameCheckView,
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    SendEmailView,
)

urlpatterns = [
    path('register/nickname-check/', NicknameCheckView.as_view(), name='nickname-check'),
    path('register/email-check/', EmailCheckAndSendCodeView.as_view(), name='email-check'),
    path('register/complete/', UserRegisterView.as_view(), name='register-complete'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('send-email/', SendEmailView.as_view(), name='send-email')
]

# 개발 환경에서만 미디어 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)