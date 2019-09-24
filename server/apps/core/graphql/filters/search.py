# -*- coding: utf-8 -*-

import operator
from functools import reduce

from django_filters import CharFilter

from django.db.models.constants import LOOKUP_SEP
from django.db.models import Q, QuerySet
from django.utils import six


class SearchFilter(CharFilter):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.fields = kwargs.pop('fields', {})

    def filter(self, queryset, value) -> QuerySet:
        if not value or not self.fields:
            return queryset

        return queryset.filter(self._construct_condition(value))

    def _construct_condition(self, value) -> Q:
        orm_lookups = [
            self._construct_search(search_field)
            for search_field in self.fields
        ]
        queries = [
            Q(**{orm_lookup: value})
            for orm_lookup in orm_lookups
        ]

        return reduce(operator.or_, queries)

    @staticmethod
    def _construct_search(search_field) -> str:
        return LOOKUP_SEP.join([six.text_type(search_field), 'icontains'])
