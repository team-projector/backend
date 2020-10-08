from django.core.management import BaseCommand
from django.db import models

from apps.development.models.note import NoteType
from apps.payroll.models import SpentTime


class Command(BaseCommand):
    """Cleanup labels."""

    def handle(self, *args, **options) -> None:  # noqa: WPS110, WPS210
        """Call function."""
        query = models.Q(note__type=NoteType.TIME_SPEND) | models.Q(
            note__type=NoteType.RESET_SPEND,
        )
        SpentTime.objects.filter(note__isnull=False).exclude(query).delete()

        self.stdout.write("Clearing is complete!")
