from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.models import Issue, Label, Note, Project, ProjectGroup


class ProjectFilter(AutocompleteFilter):
    title = 'Project'
    field_name = 'project'


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
    list_display = ('title', 'employee', 'created_at', 'gl_url', 'gl_last_sync')
    search_fields = ('title', 'gl_id')
    list_filter = (ProjectFilter,)
    sortable_by = ('gl_last_sync', 'created_at')
    autocomplete_fields = ('project', 'employee')

    class Media:
        pass


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    list_display = ('type', 'created_at', 'user')
