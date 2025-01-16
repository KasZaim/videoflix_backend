from rest_framework import serializers
from django.contrib.auth import get_user_model

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model.

    This serializer is designed to handle the serialization and deserialization 
    of user data. It works with the active user model, making it compatible 
    with custom user models.
    """
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']
        
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = get_user_model()
        fields = ['email','password', 'repeated_password']
        # extra_kwargs= {
        #     'password':{
        #         'write_only': True
        #     }
        # }
    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value
    
    def save(self):
        email = self.validated_data['email']
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        self.validated_data['username'] = email
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'repeated_password':['The passwords do not match']})
        
        user = get_user_model().objects.create_user(
            email=email,
            username=email,
            password=pw,
            
        )
        user.is_active = False
        user.save()
        return user