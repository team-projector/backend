from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.users.admin.filters import UserFilter
from .filters import ProjectFilter, TeamFilter
from .inlines import NoteInline, TeamMemberInline
from ..models import Issue, Label, Note, Project, ProjectGroup, Team, TeamMember


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
class ProjectGroupAdmin(BaseModelAdmin):
    list_display = ('title', 'parent', 'gl_url', 'gl_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('parent',)


@admin.register(Project)
class ProjectAdmin(BaseModelAdmin):
    list_display = ('title', 'group', 'gl_url', 'gl_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('group',)


@admin.register(Issue)
class IssueAdmin(BaseModelAdmin):
    list_display = ('title', 'user', 'created_at', 'gl_url', 'gl_last_sync')
    list_filter = (ProjectFilter,)
    search_fields = ('title', 'gl_id')
    sortable_by = ('gl_last_sync', 'created_at')
    ordering = ('-gl_last_sync',)
    autocomplete_fields = ('project', 'user')
    inlines = (NoteInline,)


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    list_display = ('type', 'created_at', 'user')
    search_fields = ('user__login',)