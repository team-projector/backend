# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.inlines import ProjectMemberInline
from apps.development.models import ProjectGroup
from apps.development.tasks import sync_project_group_task


@admin.register(ProjectGroup)
class ProjectGroupAdmin(
    ForceSyncEntityMixin,
    BaseModelAdmin,
):
    """A class representing Project Group model for admin dashboard."""

    list_display = ('title', 'parent', 'is_active', 'gl_url', 'gl_last_sync')
    list_filter = ('is_active',)
    search_fields = ('title',)
    inlines = (ProjectMemberInline,)

    def sync_handler(self, project_group):
        """Syncing group."""
        sync_project_group_task.delay(project_group.gl_id)
