import logging
from typing import Optional

from apps.users.models import User

SYSTEM_USERNAME = "system"

logger = logging.getLogger(__name__)


def create_system_user() -> None:
    """Create system user if need."""
    _, created = User.objects.get_or_create(
        login=SYSTEM_USERNAME,
        defaults={
            "is_active": False,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    if created:
        logger.info("System user created")


def get_system_user() -> Optional[User]:
    """Get system user."""
    return User.objects.get(login=SYSTEM_USERNAME)
