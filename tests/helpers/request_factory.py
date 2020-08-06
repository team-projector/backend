# -*- coding: utf-8 -*-

from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.test.client import RequestFactory as DjangoRequestFactory

from apps.users.models import Token, User
from apps.users.services.token.create import create_user_token


class _MockStorageMessages:
    """Mock storage messages."""

    def add(self, level, message, extra_tags):
        """Mocked add."""


class RequestFactory(DjangoRequestFactory):
    """Request factory."""

    def __init__(self, *args, **kwargs) -> None:
        """Initializing."""
        super().__init__(*args, **kwargs)

        self._user: Optional[User] = None
        self._token: Optional[Token] = None

    def set_user(self, user: User, token: Optional[Token] = None) -> None:
        """Set user for auth requests."""
        self._user = user

        if token is None:
            token = create_user_token(user)

        self._token = token

    def get(self, *args, **kwargs):
        """Construct a GET request."""
        request = super().get(*args, **kwargs)
        self._auth_if_need(request)

        return request

    def post(self, *args, **kwargs):
        """Construct a POST request."""
        request = super().post(*args, **kwargs)
        request._dont_enforce_csrf_checks = True  # noqa: WPS437
        request._messages = _MockStorageMessages()  # noqa: WPS437
        self._auth_if_need(request)

        return request

    def _auth_if_need(self, request: HttpRequest) -> None:
        request.user = self._user or AnonymousUser()
        request.auth = self._token
