from django.core.management.base import BaseCommand

from apps.development.models import Label


class Command(BaseCommand):
    """Remove not used labels."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        deleted, _ = Label.objects.filter(
            merge_requests__isnull=True,
            issues__isnull=True,
        ).delete()
        self.stdout.write("{0} labels were removed.".format(deleted))
