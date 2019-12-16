# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.users.services.token.clear import clear_tokens


class Command(BaseCommand):
    """Clear tokens command."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        clear_tokens()
