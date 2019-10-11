# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.tasks import sync_project

from ..models import Project
from .inlines import ProjectMemberInline


@admin.register(Project)
class ProjectAdmin(
    ForceSyncEntityMixin,
    BaseModelAdmin,
):
    """A class representing Project model for admin dashboard."""

    list_display = ('title', 'group', 'gl_url', 'gl_last_sync')
    search_fields = ('title', 'group__title', 'gl_url')
    inlines = (ProjectMemberInline,)

    def sync_handler(self, project):
        """Syncing project."""
        sync_project.delay(
            project.group.id,
            project.gl_id,
            project.id,
        )
