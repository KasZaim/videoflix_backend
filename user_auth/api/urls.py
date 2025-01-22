from django.urls import path
from .views import RegistrationView, EmailConfirmationView,LoginView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('confirm-email/<uidb64>/<token>/', EmailConfirmationView.as_view(), name='email-confirmation'),
    path('login/', LoginView.as_view(), name='login'),
    ]
