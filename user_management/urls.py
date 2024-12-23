from django.urls import path
from .views import (
    EmailCheckAndSendCodeView,
    NicknameCheckView,
    UserRegisterView,
    UserLoginView,
    UserProfileView,
)

urlpatterns = [
    path('register/nickname-check/', NicknameCheckView.as_view(), name='nickname-check'),
    path('register/email-check/', EmailCheckAndSendCodeView.as_view(), name='email-check'),
    path('register/complete/', UserRegisterView.as_view(), name='register-complete'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
]