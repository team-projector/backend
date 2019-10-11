# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.tasks import sync_group_milestone, sync_project_milestone

from ..models import Milestone, Project, ProjectGroup


@admin.register(Milestone)
class MilestoneAdmin(
    ForceSyncEntityMixin,
    BaseModelAdmin,
):
    """A class representing Milestone model for admin dashboard."""

    list_display = ('id', 'title', 'start_date', 'due_date', 'budget', 'state')
    search_fields = ('title',)

    def sync_handler(self, milestone):
        """Syncing milestone."""
        if milestone.content_type.model_class() == Project:
            sync_project_milestone.delay(
                milestone.owner.gl_id,
                milestone.gl_id,
            )
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_group_milestone.delay(
                milestone.owner.gl_id,
                milestone.gl_id,
            )
