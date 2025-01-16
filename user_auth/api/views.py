from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from .serializers import RegistrationSerializer, CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

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
            confirmation_link = request.build_absolute_uri(
                reverse('email-confirmation',
                        kwargs={'uidb64': uid, 'token': token})
            )

            try:
                html_message = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center;">
                        <img src="{request.build_absolute_uri('../static/images/Logo.png')}" alt="Videoflix" width="150">
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
        uid = urlsafe_base64_encode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return Response({"message": "Ungültiger oder abgelaufener Link."}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"message": "E-Mail erfolgreich bestätigt. Dein Konto ist jetzt aktiv."}, status=status.HTTP_200_OK)
    return Response({"message": "Ungültiger oder abgelaufener Link."}, status=status.HTTP_400_BAD_REQUEST)
