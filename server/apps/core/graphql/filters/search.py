# -*- coding: utf-8 -*-

import operator
from functools import reduce

from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.utils import six
from django_filters import CharFilter


class SearchFilter(CharFilter):
    """Search filter."""

    def __init__(self, *args, **kwargs):
        """Initialize self."""
        super().__init__()
        self.fields = kwargs.pop("fields", {})

    def filter(self, queryset, search_value) -> models.QuerySet:  # noqa: A003
        """Do filtering."""
        if not search_value or not self.fields:
            return queryset

        return queryset.filter(self._construct_condition(search_value))

    def _construct_condition(self, search_value) -> models.Q:
        orm_lookups = [
            self._construct_search(search_field)
            for search_field in self.fields
        ]
        queries = [
            models.Q(**{orm_lookup: search_value})
            for orm_lookup in orm_lookups
        ]

        return reduce(operator.or_, queries)

    def _construct_search(self, search_field) -> str:
        field = six.text_type(search_field)

        if field.startswith("^"):
            search_type = "istartswith"
            field = field[1:]

        elif field.startswith("="):
            search_type = "iexact"
            field = field[1:]
        else:
            search_type = "icontains"

        return LOOKUP_SEP.join([field, search_type])
