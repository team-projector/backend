import abc
from dataclasses import dataclass

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.application.errors import BaseApplicationError
from apps.core.application.use_cases import BaseUseCase
from apps.core.injector import injector
from apps.users.application.interfaces import ITokenService
from apps.users.models import Token


@dataclass(frozen=True)
class LoginInputDto:
    """Login unput data."""

    username: str
    password: str


@dataclass(frozen=True)
class LoginOutputDto:
    """Login output data."""

    token: Token


class LoginError(BaseApplicationError, metaclass=abc.ABCMeta):
    """Base class for login errors."""


class EmptyCredentialsError(LoginError):
    """Empty credentials error."""

    code = "empty_credentials"
    message = _("MSG__MUST_INCLUDE_LOGIN_AND_PASSWORD")


class AuthenticationError(LoginError):
    """Wrong credentials error."""

    code = "authentication_failed"
    message = _("MSG__UNABLE_TO_LOGIN_WITH_PROVIDED_CREDENTIALS")


class LoginUseCase(BaseUseCase[LoginInputDto, LoginOutputDto]):
    """Login process."""

    def execute(self, input_dto: LoginInputDto) -> None:
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

        token_service = injector.get(ITokenService)
        token = token_service.create_user_token(user)

        self.presenter.present(LoginOutputDto(token=token))

    def _validate_input(self, input_dto: LoginInputDto) -> None:
        if not input_dto.username or not input_dto.password:
            raise EmptyCredentialsError
