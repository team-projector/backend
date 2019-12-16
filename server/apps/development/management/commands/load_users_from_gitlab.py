# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.users.services.user.gl.manager import UserGlManager


class Command(BaseCommand):
    """Sync users with gitlab."""

    def handle(self, *args, **options):
        """Call function."""
        UserGlManager().sync_users()
