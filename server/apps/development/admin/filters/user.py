# -*- coding: utf-8 -*-

from jnt_admin_tools.autocomplete_filter import AutocompleteFilter


class UserFilter(AutocompleteFilter):
    """Autocomplete filter by ticket."""

    title = "User"
    field_name = "user"
