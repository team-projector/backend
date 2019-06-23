from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import ForceSyncEntityMixin
from apps.development.admin.filters import MilestoneFilter, TeamFilter
from apps.development.tasks import (
    sync_group_milestone, sync_project, sync_project_group, sync_project_issue,
    sync_project_merge_request, sync_project_milestone
)
from apps.users.admin.filters import UserFilter
from .filters import ProjectFilter
from .inlines import NoteInline, ProjectMemberInline, TeamMemberInline
from ..models import (
    Feature, Issue, Label, MergeRequest, Milestone, Note, Project, ProjectGroup,
    ProjectMember, Team, TeamMember
)


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
    inlines = (ProjectMemberInline,)

    def sync_handler(self, obj):
        sync_project_group.delay(obj.gl_id)


@admin.register(Project)
class ProjectAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = ('title', 'group', 'gl_url', 'gl_last_sync')
    search_fields = ('title', 'group__title', 'gl_url')
    autocomplete_fields = ('group',)
    inlines = (ProjectMemberInline,)

    def sync_handler(self, obj):
        sync_project.delay(obj.group.id, obj.gl_id, obj.id)


@admin.register(Issue)
class IssueAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = (
        'title', 'user', 'milestone', 'state', 'created_at', 'gl_last_sync'
    )
    list_filter = (ProjectFilter, MilestoneFilter, 'state')
    search_fields = ('title', 'gl_id')
    sortable_by = ('gl_last_sync', 'created_at')
    ordering = ('-gl_last_sync',)
    autocomplete_fields = (
        'project', 'user', 'milestone', 'feature', 'labels', 'participants'
    )
    inlines = (NoteInline,)

    def sync_handler(self, obj):
        sync_project_issue.delay(obj.project.gl_id, obj.gl_iid)


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    list_display = ('type', 'created_at', 'user')
    search_fields = ('user__login',)


@admin.register(Milestone)
class MilestoneAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'budget', 'state')
    search_fields = ('title',)

    def sync_handler(self, obj):
        if obj.content_type.model_class() == Project:
            sync_project_milestone.delay(obj.owner.gl_id, obj.gl_id)
        elif obj.content_type.model_class() == ProjectGroup:
            sync_group_milestone.delay(obj.owner.gl_id, obj.gl_id)


@admin.register(ProjectMember)
class ProjectMemberAdmin(BaseModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user', 'role')


@admin.register(Feature)
class FeatureAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'budget')
    search_fields = ('title',)


@admin.register(MergeRequest)
class MergeRequestAdmin(ForceSyncEntityMixin, BaseModelAdmin):
    list_display = (
        'title', 'assignee', 'author', 'state', 'created_at', 'gl_last_sync'
    )
    list_filter = (ProjectFilter,)
    search_fields = ('title', 'gl_id')
    sortable_by = ('gl_last_sync', 'created_at')
    ordering = ('-gl_last_sync',)
    autocomplete_fields = (
        'project', 'assignee', 'author', 'milestone', 'labels'
    )
    inlines = (NoteInline,)

    def sync_handler(self, obj):
        sync_project_merge_request.delay(obj.project.gl_id, obj.gl_iid)
