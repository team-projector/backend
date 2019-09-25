# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.tasks import sync_group_milestone, sync_project_milestone

from ..models import Milestone, Project, ProjectGroup


@admin.register(Milestone)
class MilestoneAdmin(ForceSyncEntityMixin,
                     BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'budget', 'state')
    search_fields = ('title',)

    def sync_handler(self, obj):
        if obj.content_type.model_class() == Project:
            sync_project_milestone.delay(
                obj.owner.gl_id,
                obj.gl_id,
            )
        elif obj.content_type.model_class() == ProjectGroup:
            sync_group_milestone.delay(
                obj.owner.gl_id,
                obj.gl_id,
            )
