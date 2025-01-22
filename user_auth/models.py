from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    custom = models.CharField(max_length=1000, default= '')
    phone = models.CharField(max_length=20, default= '')
    adress = models.CharField(max_length=150, default= '')
    is_email_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']