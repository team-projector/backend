from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.models import Issue, Project, ProjectGroup


@admin.register(ProjectGroup)
class ProjectGroupAdmin(BaseModelAdmin):
    list_display = ('title', 'parent', 'gitlab_url', 'gitlab_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('parent',)


@admin.register(Project)
class ProjectAdmin(BaseModelAdmin):
    list_display = ('title', 'gitlab_url', 'gitlab_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('group',)


@admin.register(Issue)
class IssueAdmin(BaseModelAdmin):
    list_display = ('title', 'gitlab_url', 'gitlab_last_sync')
    search_fields = ('title',)
    autocomplete_fields = ('project', 'employee')
