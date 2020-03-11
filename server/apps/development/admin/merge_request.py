# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import ProjectFilter
from apps.development.admin.inlines import NoteInline
from apps.development.models import MergeRequest
from apps.development.tasks import sync_project_merge_request_task


@admin.register(MergeRequest)
class MergeRequestAdmin(
    ForceSyncEntityMixin, BaseModelAdmin,
):
    """A class representing Merge Request model for admin dashboard."""

    list_display = (
        "title",
        "user",
        "author",
        "state",
        "created_at",
        "gl_last_sync",
    )
    list_filter = (ProjectFilter,)
    search_fields = ("title", "gl_id")
    sortable_by = ("gl_last_sync", "created_at")
    ordering = ("-gl_last_sync",)
    inlines = (NoteInline,)

    def sync_handler(self, merge_request):
        """Syncing merge request."""
        sync_project_merge_request_task.delay(
            merge_request.project.gl_id, merge_request.gl_iid,
        )
