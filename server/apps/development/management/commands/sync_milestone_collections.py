from django.core.management.base import BaseCommand
from tqdm import tqdm

from apps.development.models import Project, ProjectGroup
from apps.development.services.milestone.gl.manager import (  # noqa: WPS450
    _milestones_syncer,
)
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)

project_provider = ProjectGlProvider()
group_provider = ProjectGroupGlProvider()


class Command(BaseCommand):
    """Sync users with gitlab."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Call main function."""
        self._sync_project_milestones()
        self._sync_groups_milestones()

    def _sync_project_milestones(self) -> None:
        """Sync milestones for project."""
        queryset = Project.objects.filter(is_active=True)
        data_for_sync = {
            "iterable": queryset,
            "total": queryset.count(),
            "desc": "Sync milestones for projects...",
        }

        for project in tqdm(**data_for_sync):
            gl_work_item = project_provider.get_gl_project(project)
            if not gl_work_item:
                continue
            _milestones_syncer.sync_all_milestones(
                gl_work_item=gl_work_item,
                work_item=project,
            )

    def _sync_groups_milestones(self) -> None:
        """Sync milestones for project groups."""
        queryset = ProjectGroup.objects.filter(is_active=True)
        data_for_sync = {
            "iterable": queryset,
            "total": queryset.count(),
            "desc": "Sync milestones for project groups...",
        }

        for group in tqdm(**data_for_sync):
            gl_work_item = group_provider.get_gl_group(group)
            if not gl_work_item:
                continue
            _milestones_syncer.sync_all_milestones(
                gl_work_item=group_provider.get_gl_group(group),
                work_item=group,
            )
