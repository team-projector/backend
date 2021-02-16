import abc
from typing import Tuple

from apps.users.models import User


class IUserMetricsService(abc.ABC):
    """User metrics provider service."""

    @abc.abstractmethod
    def get_metrics(self, user: User, fields: Tuple[str, ...] = ()):
        """Calculate user metrics."""
