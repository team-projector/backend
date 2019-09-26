# -*- coding: utf-8 -*-

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as DrfTokenAuth

from apps.users.models import Token


class TokenAuthentication(DrfTokenAuth):
    keyword = 'Bearer'
    model = Token

    def authenticate_credentials(self, key: str):
        user, token = super().authenticate_credentials(key)

        if self._is_expired(token):
            raise exceptions.AuthenticationFailed('Token has expired')

        return user, token

    def _is_expired(self, token) -> bool:
        return token.created < timezone.now() - timedelta(
            minutes=settings.TOKEN_EXPIRE_PERIOD,
        )
