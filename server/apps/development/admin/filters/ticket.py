# -*- coding: utf-8 -*-

from admin_tools.autocomplete_filter import AutocompleteFilter


class TicketFilter(AutocompleteFilter):
    """Autocomplete filter by ticket."""

    title = "Ticket"
    field_name = "ticket"
