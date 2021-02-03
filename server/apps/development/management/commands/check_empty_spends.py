from django.core.management import BaseCommand

from apps.development.models import Note
from apps.development.models.note import NoteType


class Command(BaseCommand):
    """Cleanup labels."""

    def handle(self, *args, **options):
        notes = Note.objects.filter(
            type=NoteType.TIME_SPEND,
            time_spend__isnull=True,
        )
        if not notes.exists():
            return

        self.stdout.write("Found {0} items".format(notes.count()))
        for note in notes.order_by("user"):
            self.stdout.write(
                "{0} -> {1} [object.pk={2}][note.pk={3}]".format(
                    note.content_type, note.content_object, note.object_id, note.pk,
                ),
            )
