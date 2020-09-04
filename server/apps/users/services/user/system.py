# -*- coding: utf-8 -*-

from typing import Optional

from apps.users.models import User

SYSTEM_USERNAME = "system"


def create_system_user() -> None:
    """Create system user if need."""
    User.objects.get_or_create(
        login=SYSTEM_USERNAME,
        defaults={
            "is_active": False,
            "is_staff": False,
            "is_superuser": False,
        },
    )


def get_system_user() -> Optional[User]:
    """Get system user."""
    return User.objects.get(login=SYSTEM_USERNAME)
