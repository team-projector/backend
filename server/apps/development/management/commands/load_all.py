from django.core.management.base import BaseCommand

from apps.development.tasks import sync_all_task


class Command(BaseCommand):
    """Load groups from gitlab."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        sync_all_task()
