from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    fieldsets = (
        (
            'individuelle Daten',
            {
                'fields': (
                    'custom',
                    'phone',
                    'adress'
                )
            }
        ),
        *UserAdmin.fieldsets,
    )