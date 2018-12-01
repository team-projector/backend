from datetime import timedelta

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from apps.users.models import Token
from server import settings

EXPIRE_MINUTES = settings.REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES


class ExpiringTokenAuthentication(TokenAuthentication):
    def get_model(self):
        return Token

    def authenticate_credentials(self, key):
        try:
            model = self.get_model()
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        if token.created < timezone.now() - timedelta(minutes=EXPIRE_MINUTES):
            raise exceptions.AuthenticationFailed('Token has expired')

        return token.user, token
