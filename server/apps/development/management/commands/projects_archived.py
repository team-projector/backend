from django.core.management.base import BaseCommand

from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState


class Command(BaseCommand):
    """All project set state archived."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        Project.objects.exclude(state=ProjectState.ARCHIVED).update(
            state=ProjectState.ARCHIVED,
        )
