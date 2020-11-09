from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import OwnerContentTypeFilter, OwnerFilter
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.tasks import (
    sync_project_group_milestone_task,
    sync_project_milestone_task,
)


@admin.register(Milestone)
class MilestoneAdmin(
    ForceSyncEntityMixin,
    BaseModelAdmin,
):
    """A class represents Milestone model for admin dashboard."""

    list_display = ("id", "title", "start_date", "due_date", "budget", "state")
    search_fields = ("title",)
    list_filter = ("state", OwnerContentTypeFilter)

    def sync_handler(self, milestone):
        """Syncing milestone."""
        if milestone.content_type.model_class() == Project:
            sync_project_milestone_task.delay(
                milestone.owner.gl_id,
                milestone.gl_id,
            )
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_project_group_milestone_task.delay(
                milestone.owner.gl_id,
                milestone.gl_id,
            )

    def get_list_filter(self, request):
        """Get list filters."""
        list_filters = super().get_list_filter(request)

        if request.GET.get("content_type__id__exact"):
            list_filters = list_filters + (OwnerFilter,)

        return list_filters

    def changelist_view(self, request: HttpRequest, extra_context=None):
        """
        The "change list" admin view for this model.

        Apply filter for object_id only with content_type.
        """
        content_type_filter = request.GET.get("content_type__id__exact")
        object_id_filter = request.GET.get("object_id__exact")

        if object_id_filter and not content_type_filter:
            query_params = [
                "{0}={1}".format(query, param)
                for query, param in request.GET.items()
                if query != "object_id__exact"
            ]

            return redirect(
                "{0}?{1}".format(request.path, "&".join(query_params)),
            )

        return super().changelist_view(request, extra_context=extra_context)
