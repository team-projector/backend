import abc

from apps.core.errors import BaseError


class BaseApplicationError(BaseError, metaclass=abc.ABCMeta):
    """Base exception for application errors."""


class AuthenticationErrorMixin(BaseApplicationError):
    """Mark the error as authentication error."""


class AccessDeniedErrorMixin(BaseApplicationError):
    """Mark the error as forbid error."""
