# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models.milestone import MILESTONE_STATES


class ActiveFilter(django_filters.BooleanFilter):
    def filter(self, queryset, value) -> QuerySet:
        if value is None:
            return queryset

        return queryset.filter(
            state=MILESTONE_STATES.active if value else MILESTONE_STATES.closed,
        )


class MilestonesFilterSet(django_filters.FilterSet):
    active = ActiveFilter()

    order_by = OrderingFilter(
        fields=('due_date',),
    )
