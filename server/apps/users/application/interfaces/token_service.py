import abc

from apps.users.models import Token, User


class ITokenService(abc.ABC):
    """Service for manage tokens."""

    @abc.abstractmethod
    def create_user_token(self, user: User) -> Token:
        """Create token for user."""

    @abc.abstractmethod
    def clear_tokens(self) -> None:
        """Deletes expired tokens."""
