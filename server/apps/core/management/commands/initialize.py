import os

from django.contrib.auth.management.commands import createsuperuser
from django.core import management
from django.core.management.base import BaseCommand

from apps.users.models import User
from apps.users.services.user.system import create_system_user


class Command(BaseCommand):
    """
    Initializing system.

    Includes:
    1. create system user
    2. create super user by provided credentials via env:
    - DJANGO_SUPERUSER_PASSWORD
    - DJANGO_SUPERUSER_LOGIN
    """

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        create_system_user()

        if self._need_create_superuser():
            management.call_command(
                createsuperuser.Command(),
                interactive=False,
            )

    def _need_create_superuser(self) -> bool:
        username = os.environ.get("DJANGO_SUPERUSER_LOGIN")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not username or not password:
            return False

        try:
            User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return True
        else:
            return False
