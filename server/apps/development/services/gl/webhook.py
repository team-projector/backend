from abc import ABC, abstractmethod
from typing import Optional


class BaseGLWebhook(ABC):
    """Base class for gitlab webhooks."""

    object_kind: Optional[str] = None
    settings_field: Optional[str] = None

    @abstractmethod
    def handle_hook(self, body) -> None:
        """Handle webhook message."""
