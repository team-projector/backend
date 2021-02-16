import abc
from typing import Iterable

from apps.users.models import User


class IUserProblemsService(abc.ABC):
    """Provide information about user problems."""

    @abc.abstractmethod
    def get_problems(self, user: User) -> Iterable[str]:
        """Get user problems."""
