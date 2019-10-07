# -*- coding: utf-8 -*-

from admin_tools.autocomplete_filter import AutocompleteFilter


class MilestoneFilter(AutocompleteFilter):
    """Autocomplete filter by milestone."""

    title = 'Milestone'
    field_name = 'milestone'
