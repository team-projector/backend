from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import TeamFilter
from apps.development.tasks import sync_project_issue, sync_project, sync_project_group
from apps.users.admin.filters import UserFilter
from .filters import ProjectFilter
from .inlines import NoteInline, TeamMemberInline
from ..models import Issue, Label, Note, Project, ProjectGroup, Team, TeamMember, Milestone, ProjectMember, Epic


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    inlines = (TeamMemberInline,)


@admin.register(TeamMember)
class TeamMemberAdmin(BaseModelAdmin):
    list_display = ('team', 'user')
    search_fields = ('team', 'user')
    list_filter = (TeamFilter, UserFilter)
    autocomplete_fields = ('team', 'user')


@admin.register(Label)
class LabelAdmin(BaseModelAdmin):
    list_display = ('title', 'color')
    search_fields = ('title',)


@admin.register(ProjectGroup)
class ProjectGroupAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = ('title', 'parent', 'gl_url', 'gl_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('parent',)

    def sync_handler(self, obj):
        sync_project_group.delay(obj.gl_id)


@admin.register(Project)
class ProjectAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = ('title', 'group', 'gl_url', 'gl_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('group',)

    def sync_handler(self, obj):
        sync_project.delay(obj.group, obj.gl_id, obj.id)


@admin.register(Issue)
class IssueAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = ('title', 'user', 'created_at', 'gl_url', 'gl_last_sync')
    list_filter = (ProjectFilter,)
    search_fields = ('title', 'gl_id')
    sortable_by = ('gl_last_sync', 'created_at')
    ordering = ('-gl_last_sync',)
    autocomplete_fields = ('project', 'user', 'milestone', 'labels', 'participants')
    inlines = (NoteInline,)

    def sync_handler(self, obj):
        sync_project_issue.delay(obj.project.gl_id, obj.gl_iid)


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    list_display = ('type', 'created_at', 'user')
    search_fields = ('user__login',)


@admin.register(Milestone)
class MilestoneAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'budget')
    search_fields = ('title',)


@admin.register(ProjectMember)
class ProjectMemberAdmin(BaseModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user', 'role')


@admin.register(Epic)
class EpicAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'budget')
    search_fields = ('title',)
