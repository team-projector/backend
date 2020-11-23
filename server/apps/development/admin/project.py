from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import TeamFilter
from apps.development.admin.inlines import ProjectMemberInline
from apps.development.models import Project
from apps.development.tasks import sync_project_task


@admin.register(Project)
class ProjectAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    """A class represents Project model for admin dashboard."""

    list_display = (
        "title",
        "group",
        "is_active",
        "state",
        "gl_url",
        "gl_last_sync",
    )
    list_filter = ("state", "is_active", TeamFilter)
    search_fields = ("title", "group__title", "gl_url")
    inlines = (ProjectMemberInline,)

    def sync_handler(self, project):
        """Syncing project."""
        sync_project_task.delay(
            project.group.id,
            project.id,
        )
