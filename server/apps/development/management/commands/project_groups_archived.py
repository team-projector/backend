from django.core.management.base import BaseCommand

from apps.development.models import ProjectGroup
from apps.development.models.choices.project_state import ProjectState


class Command(BaseCommand):
    """All project groups set state archived."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        ProjectGroup.objects.exclude(state=ProjectState.ARCHIVED).update(
            state=ProjectState.ARCHIVED,
        )
