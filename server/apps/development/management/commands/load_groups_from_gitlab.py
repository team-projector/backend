from constance import config
from django.core.management.base import BaseCommand

from apps.development.services.project_group.gl.manager import (
    ProjectGroupGlManager,
)
from apps.development.tasks import sync_groups_milestones_task


class Command(BaseCommand):
    """Load groups from gitlab."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call function."""
        ProjectGroupGlManager().sync_groups(
            filter_ids=config.GITLAB_ROOT_GROUPS or (),
        )
        sync_groups_milestones_task()
