from django.urls import path
from .views import UserRegistrationView, EmailVerificationView, UserLoginView, SendEmailCodeView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('send-code/', SendEmailCodeView.as_view(), name='send-code'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('<int:user_id>/', UserProfileView.as_view(), name='user-profile')
]