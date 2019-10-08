# -*- coding: utf-8 -*-

from admin_tools.autocomplete_filter import AutocompleteFilter


class TeamFilter(AutocompleteFilter):
    """Autocomplete filter by team."""

    title = 'Team'
    field_name = 'team'
