# -*- coding: utf-8 -*-

from jnt_admin_tools.autocomplete_filter import AutocompleteFilter


class ProjectFilter(AutocompleteFilter):
    """Autocomplete filter by project."""

    title = "Project"
    field_name = "project"
