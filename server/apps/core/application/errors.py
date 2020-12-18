import abc


class BaseApplicationError(Exception, metaclass=abc.ABCMeta):
    """Base exception for usecase errors."""

    code: str
    message: str

    def __init__(self):
        """Initialize."""
        super().__init__(self.message)


class AuthenticationErrorMixin(BaseApplicationError):
    """Mark the error as authentication error."""


class AccessDeniedErrorMixin(BaseApplicationError):
    """Mark the error as forbid error."""
