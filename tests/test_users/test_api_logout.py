from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status

from apps.users.models import Token
from apps.users.utils.token import create_user_token
from tests.base import BaseAPITest


class LogoutTests(BaseAPITest):
    def test_logout(self):
        self.set_credentials()

        response = self.client.post('/api/logout')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_no_auth(self):
        response = self.client.post('/api/logout')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_token(self):
        token = create_user_token(self.user)
        token.created = timezone.now() - timedelta(minutes=settings.REST_FRAMEWORK_TOKEN_EXPIRE + 60)
        token.save()

        self.set_credentials(token=token)

        response = self.client.post('/api/logout')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bad_token(self):
        token = create_user_token(self.user)
        token.key += '123456'

        self.set_credentials(token=token)

        response = self.client.post('/api/logout')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
