# -*- coding: utf-8 -*-

from admin_tools.autocomplete_filter import AutocompleteFilter


class UserFilter(AutocompleteFilter):
    """Autocomplete filter by user."""

    title = "User"
    field_name = "user"
