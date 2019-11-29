# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models.milestone import MILESTONE_STATES


class ActiveFilter(django_filters.BooleanFilter):
    """Filter milestone by active state."""

    def filter(self, queryset, value) -> QuerySet:  # noqa A003
        """Do filtering."""
        if value is None:
            return queryset

        return queryset.filter(
            state=MILESTONE_STATES.ACTIVE if value else MILESTONE_STATES.CLOSED,
        )


class MilestonesFilterSet(django_filters.FilterSet):
    """Set of filters for Milestone."""

    active = ActiveFilter()

    order_by = OrderingFilter(
        fields=('due_date',),
    )
