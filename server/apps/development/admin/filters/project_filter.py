from admin_auto_filters.filters import AutocompleteFilter


class ProjectFilter(AutocompleteFilter):
    title = 'Project'
    field_name = 'project'
