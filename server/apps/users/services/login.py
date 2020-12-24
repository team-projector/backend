import abc
from dataclasses import dataclass

import injector
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.services.errors import BaseServiceError
from apps.users.models import Token
from apps.users.services.token import TokenService


@dataclass(frozen=True)
class LoginInputDto:
    """Login unput data."""

    username: str
    password: str


@dataclass(frozen=True)
class LoginOutputDto:
    """Login output data."""

    token: Token


class LoginError(BaseServiceError, metaclass=abc.ABCMeta):
    """Base class for login errors."""


class EmptyCredentialsError(LoginError):
    """Empty credentials error."""

    code = "empty_credentials"
    message = _("MSG__MUST_INCLUDE_LOGIN_AND_PASSWORD")


class AuthenticationError(LoginError):
    """Wrong credentials error."""

    code = "authentication_failed"
    message = _("MSG__UNABLE_TO_LOGIN_WITH_PROVIDED_CREDENTIALS")


class LoginService:
    """Login service."""

    @injector.inject
    def __init__(self, token_service: TokenService):
        """Initialize."""
        self._token_service = token_service

    def execute(self, input_dto: LoginInputDto) -> Token:
        """Main logic."""
        self._validate_input(input_dto)

        user = authenticate(
            login=input_dto.username,
            password=input_dto.password,
        )

        if not user:
            raise AuthenticationError

        user.last_login = timezone.now()
        user.save(update_fields=("last_login",))

        return self._token_service.create_user_token(user)

    def _validate_input(self, input_dto: LoginInputDto) -> None:
        if not input_dto.username or not input_dto.password:
            raise EmptyCredentialsError
