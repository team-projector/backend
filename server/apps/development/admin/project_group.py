from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.tasks import sync_project_group
from .inlines import ProjectMemberInline
from ..models import ProjectGroup


@admin.register(ProjectGroup)
class ProjectGroupAdmin(ForceSyncEntityMixin,
                        BaseModelAdmin):
    list_display = ('title', 'parent', 'gl_url', 'gl_last_sync')
    search_fields = ('title',)
    inlines = (ProjectMemberInline,)

    def sync_handler(self, obj):
        sync_project_group.delay(obj.gl_id)
