from django.urls import path
from .views import UserRegistrationView, EmailVerificationView, UserLoginView, EmailVerifyRequestView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('request-verify/', EmailVerifyRequestView.as_view(), name='request-verify'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('login/', UserLoginView.as_view(), name='login'),
]