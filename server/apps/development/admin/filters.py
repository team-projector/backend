from admin_auto_filters.filters import AutocompleteFilter


class TeamFilter(AutocompleteFilter):
    title = 'Team'
    field_name = 'team'
