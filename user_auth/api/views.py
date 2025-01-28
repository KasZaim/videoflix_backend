from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from .serializers import RegistrationSerializer, CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import EmailMessage
import os
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator


User = get_user_model()

class UsersView(generics.ListAPIView):
    """
    View to list all users in the system.

    This view is restricted to admin users only and uses the `ListAPIView`
    from Django REST Framework to provide a read-only endpoint for listing users.
    """
    permission_classes = [IsAdminUser]
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer


class RegistrationView(APIView):
    """
    View for user registration with email confirmation.
    """

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generiere Token und UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            frontend_domain = os.environ.get('FRONTEND_DOMAIN')
            confirmation_link = f"{frontend_domain}/verify-email?uid={uid}&token={token}"

            try:
                html_message = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center;">
                        <img src="{request.build_absolute_uri('/static/images/logo.png')}" alt="Videoflix" width="150">
                        <h2 style="color: #4a90e2;">Bestätige deine Registrierung</h2>
                        <p>Hallo,</p>
                        <p>Vielen Dank, dass du dich bei <strong>Videoflix</strong> registriert hast. Um die Registrierung abzuschließen und deine E-Mail-Adresse zu bestätigen, klicke bitte auf den untenstehenden Button:</p>
                        <a href="{confirmation_link}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #4a90e2; text-decoration: none; border-radius: 5px;">
                            Account aktivieren
                        </a>
                        <p>Wenn du kein Konto bei uns erstellt hast, ignoriere bitte diese E-Mail.</p>
                        <p>Mit freundlichen Grüßen,<br>Dein Videoflix-Team</p>
                    </body>
                </html>
                """

                email = EmailMessage(
                    subject="Bestätige deine Registrierung",
                    body=html_message,
                    from_email=f"Videoflix Support <{settings.EMAIL_HOST_USER}>",
                    to=[user.email],
                )
                email.content_subtype = "html"  # Setzt den Inhaltstyp auf HTML
                email.send()
            except Exception as e:
                error_message = f"Failed to send confirmation email to {user.email}. Error: {str(e)}"
                return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(
                {"message": "Registrierung erfolgreich. Bitte überprüfe deine E-Mails zur Bestätigung."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailConfirmationView(APIView):
    """
    View to confirm a user's email address.
    """

    def get(self, request, uidb64, token):
        try:
            # Decodiere die UID und finde den Benutzer
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response({"message": "Ungültiger oder abgelaufener Link."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Überprüfe den Token
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            frontend_domain = os.environ.get('FRONTEND_DOMAIN')
            return Response({"redirect_url": f"{frontend_domain}/login"}, status=status.HTTP_200_OK)

        return Response({"message": "Ungültiger oder abgelaufener Link."}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    View to log in a user and return an authentication token.
    """

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Überprüfen, ob beide Felder übergeben wurden
        if not email or not password:
            return Response(
                {"error": "E-Mail und Passwort sind erforderlich."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response(
                {"error": "Ungültige E-Mail oder Passwort."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"error": "Dein Konto ist inaktiv. Bitte bestätige deine E-Mail-Adresse."},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        data = {}

        token, created = Token.objects.get_or_create(user=user)

        data = {
            'token': token.key,
            'username': user.username,
            'user_id': user.id
        }

        return Response(data, status=status.HTTP_200_OK)



class ForgotPasswordView(APIView):
    """
    View to handle forgot password requests.
    """

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "E-Mail-Adresse wird benötigt."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Kein Benutzer mit dieser E-Mail-Adresse gefunden."}, status=status.HTTP_404_NOT_FOUND)

        # Token und UID generieren
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        frontend_domain = os.environ.get('FRONTEND_DOMAIN', 'http://localhost:4200')
        reset_link = f"{frontend_domain}/reset-password?uid={uid}&token={token}"

        # E-Mail senden
        subject = "Passwort zurücksetzen - Videoflix"
        message = f"""
        Hallo {user.username},

        Du hast angefragt, dein Passwort zurückzusetzen. Klicke auf den folgenden Link, um dein Passwort zurückzusetzen:

        {reset_link}

        Wenn du dies nicht angefordert hast, ignoriere diese Nachricht.

        Mit freundlichen Grüßen,
        Dein Videoflix-Team
        """
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
        email.send()

        return Response({"message": "Passwort-Reset-Link wurde an die E-Mail-Adresse gesendet."}, status=status.HTTP_200_OK)

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password

class ResetPasswordView(APIView):
    """
    View to handle password reset requests.
    """

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uid or not token or not new_password:
            return Response({"error": "Alle Felder sind erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Ungültige Benutzer-ID."}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Ungültiger oder abgelaufener Token."}, status=status.HTTP_400_BAD_REQUEST)

        # Passwort setzen und speichern
        user.password = make_password(new_password)
        user.save()

        return Response({"message": "Passwort erfolgreich zurückgesetzt."}, status=status.HTTP_200_OK)
