import abc

from apps.core.errors import BaseError


class BaseServiceError(BaseError, metaclass=abc.ABCMeta):
    """Base exception for services errors."""
