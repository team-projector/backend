from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.models import Issue, Project, ProjectGroup


class ProjectFilter(AutocompleteFilter):
    title = 'Project'
    field_name = 'project'


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
    list_display = ('title', 'employee', 'created_at', 'gl_url', 'gl_last_sync')
    search_fields = ('title',)
    list_filter = (ProjectFilter,)
    sortable_by = ('gl_last_sync', 'created_at')
    autocomplete_fields = ('project', 'employee')

    class Media:
        pass
