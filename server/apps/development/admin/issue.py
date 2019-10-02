# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import MilestoneFilter
from apps.development.tasks import sync_project_issue

from ..models import Issue
from .filters import ProjectFilter
from .inlines import NoteInline


@admin.register(Issue)
class IssueAdmin(
    ForceSyncEntityMixin,
    BaseModelAdmin,
):
    list_display = (
        'title', 'user', 'milestone', 'state', 'created_at', 'gl_last_sync',
    )
    list_filter = (ProjectFilter, MilestoneFilter, 'state')
    search_fields = ('title', 'gl_id')
    sortable_by = ('gl_last_sync', 'created_at')
    ordering = ('-gl_last_sync',)
    inlines = (NoteInline,)

    def sync_handler(self, obj):
        """
        Syncing current issue.
        """
        sync_project_issue.delay(
            obj.project.gl_id,
            obj.gl_iid,
        )
