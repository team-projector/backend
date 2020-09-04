# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.users.services.user.system import create_system_user


class Command(BaseCommand):
    """
    Initializing system.

    Includes:
    - create system user
    - create super user by provided credentials
    """

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        create_system_user()
        self.stdout.write(self.style.SUCCESS("System user created"))
