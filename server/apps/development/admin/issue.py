# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import (
    MilestoneFilter,
    ProjectFilter,
    TicketFilter,
    UserFilter,
)
from apps.development.admin.inlines import NoteInline
from apps.development.models import Issue
from apps.development.tasks import sync_project_issue_task


@admin.register(Issue)
class IssueAdmin(
    ForceSyncEntityMixin, BaseModelAdmin,
):
    """A class representing Issue model for admin dashboard."""

    list_display = (
        "title",
        "user",
        "milestone",
        "state",
        "created_at",
        "gl_last_sync",
    )
    list_filter = (
        ProjectFilter,
        MilestoneFilter,
        TicketFilter,
        UserFilter,
        "state",
    )
    search_fields = ("title", "gl_id")
    sortable_by = ("gl_last_sync", "created_at")
    ordering = ("-gl_last_sync",)
    inlines = (NoteInline,)

    def sync_handler(self, issue):
        """Syncing issue."""
        sync_project_issue_task.delay(
            issue.project.gl_id, issue.gl_iid,
        )
