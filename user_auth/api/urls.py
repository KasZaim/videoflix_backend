from django.urls import path
from .views import RegistrationView, EmailConfirmationView,LoginView,ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('confirm-email/<uidb64>/<token>/', EmailConfirmationView.as_view(), name='email-confirmation'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    ]
