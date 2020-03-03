# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet

from apps.core.graphql.filters import SearchFilter
from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models.milestone import Milestone, MilestoneState


class ActiveFilter(django_filters.BooleanFilter):
    """Filter milestone by active state."""

    def filter(self, queryset, value) -> QuerySet:  # noqa: A003, WPS110
        """Do filtering."""
        if value is None:
            return queryset

        return queryset.filter(
            state=MilestoneState.ACTIVE if value else MilestoneState.CLOSED,
        )


class MilestonesFilterSet(django_filters.FilterSet):
    """Set of filters for Milestone."""

    active = ActiveFilter()
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("due_date",))

    class Meta:
        model = Milestone
        fields = ("active", "state")
