from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from rest_framework.authtoken.models import Token
import json
from unittest.mock import patch, MagicMock

User = get_user_model()

class RegistrationViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'repeated_password': 'testpassword123',  # Match the serializer field name
        }
    
    def test_user_registration_success(self):  # , mock_send
        """Test successful user registration"""
        
        try:
            response = self.client.post(self.register_url, self.user_data, format='json')
            
            # Print response data to debug
            print(f"Response status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"Response data: {response.data}")
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(User.objects.count(), 1)
            self.assertEqual(User.objects.get().email, 'testuser@example.com')
            self.assertFalse(User.objects.get().is_active)  # User should not be active until email is confirmed
            # mock_send.assert_called()  # Verification email should be sent
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            raise
    
    def test_user_registration_invalid_data(self):
        """Test registration with invalid data"""
        # Test with missing email
        invalid_data = {
            'password': 'testpassword123',
            'repeated_password': 'testpassword123',
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with existing email
        User.objects.create_user(username='existinguser', email='testuser@example.com', password='password123')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailConfirmationViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            is_active=False
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse('email-confirmation', kwargs={'uidb64': self.uid, 'token': self.token})
    
    def test_email_confirmation_success(self):
        """Test successful email confirmation"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIn('redirect_url', response.data)
    
    def test_email_confirmation_invalid_uid(self):
        """Test email confirmation with invalid UID"""
        invalid_url = reverse('email-confirmation', kwargs={'uidb64': 'invalid-uid', 'token': self.token})
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_email_confirmation_invalid_token(self):
        """Test email confirmation with invalid token"""
        invalid_url = reverse('email-confirmation', kwargs={'uidb64': self.uid, 'token': 'invalid-token'})
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            is_active=True
        )
    
    def test_login_success(self):
        """Test successful login"""
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('username', response.data)
        self.assertIn('user_id', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        """Test login for inactive user"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.forgot_password_url = reverse('forgot-password')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
    
    # @patch('django.core.mail.EmailMessage.send')
    def test_forgot_password_success(self):  #, mock_send
        """Test successful forgot password request"""
        # mock_send.return_value = 1  # Mock the email sending
        
        try:
            data = {'email': 'testuser@example.com'}
            response = self.client.post(self.forgot_password_url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('message', response.data)
            # mock_send.assert_called()  # Email should be sent
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            raise
    
    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.forgot_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ResetPasswordViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.reset_password_url = reverse('reset-password')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = PasswordResetTokenGenerator().make_token(self.user)
    
    def test_reset_password_success(self):
        """Test successful password reset"""
        data = {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'newtestpassword123'
        }
        response = self.client.post(self.reset_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify that the password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newtestpassword123'))
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token"""
        data = {
            'uid': self.uid,
            'token': 'invalid-token',
            'new_password': 'newtestpassword123'
        }
        response = self.client.post(self.reset_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newtestpassword123'))
    
    def test_reset_password_invalid_uid(self):
        """Test password reset with invalid UID"""
        data = {
            'uid': 'invalid-uid',
            'token': self.token,
            'new_password': 'newtestpassword123'
        }
        response = self.client.post(self.reset_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newtestpassword123'))
