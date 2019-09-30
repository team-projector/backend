# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.tasks import sync_project_merge_request

from ..models import MergeRequest
from .filters import ProjectFilter
from .inlines import NoteInline


@admin.register(MergeRequest)
class MergeRequestAdmin(
    ForceSyncEntityMixin,
    BaseModelAdmin,
):
    list_display = (
        'title', 'user', 'author', 'state', 'created_at', 'gl_last_sync',
    )
    list_filter = (ProjectFilter,)
    search_fields = ('title', 'gl_id')
    sortable_by = ('gl_last_sync', 'created_at')
    ordering = ('-gl_last_sync',)
    inlines = (NoteInline,)

    def sync_handler(self, obj):
        sync_project_merge_request.delay(
            obj.project.gl_id,
            obj.gl_iid,
        )
