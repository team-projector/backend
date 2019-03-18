from admin_auto_filters.filters import AutocompleteFilter


class ProjectFilter(AutocompleteFilter):
    title = 'Project'
    field_name = 'project'


class TeamFilter(AutocompleteFilter):
    title = 'Team'
    field_name = 'team'
