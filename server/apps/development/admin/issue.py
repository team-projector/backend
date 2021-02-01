from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.inlines import NoteInline
from apps.development.models import Issue
from apps.development.tasks import (
    propagate_ticket_to_related_issues_task,
    sync_project_issue_task,
)


@admin.register(Issue)
class IssueAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    """A class represents Issue model for admin dashboard."""

    list_display = (
        "title",
        "user",
        "milestone",
        "state",
        "created_at",
        "gl_last_sync",
    )
    list_filter = (
        "state",
        "project",
        "milestone",
        "ticket",
        "user",
        "author",
        "participants",
    )
    search_fields = ("title", "gl_id")
    sortable_by = ("gl_last_sync", "created_at")
    ordering = ("-gl_last_sync",)
    inlines = (NoteInline,)
    date_hierarchy = "due_date"

    def sync_handler(self, issue):
        """Syncing issue."""
        sync_project_issue_task.delay(
            issue.project.gl_id,
            issue.gl_iid,
        )

    def save_model(self, request, instance, form, change):
        """On save model."""
        super().save_model(request, instance, form, change)
        if "ticket" in form.changed_data:
            propagate_ticket_to_related_issues_task.delay(issue_id=instance.pk)
