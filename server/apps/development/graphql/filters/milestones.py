# -*- coding: utf-8 -*-

import django_filters
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.filters import OrderingFilter, SearchFilter

from apps.development.models.milestone import Milestone, MilestoneState


class ActiveFilter(django_filters.BooleanFilter):
    """Filter milestone by active state."""

    def filter(  # noqa: WPS125, A003
        self, queryset, value,  # noqa: WPS110
    ) -> QuerySet:
        """Do filtering."""
        if value is None:
            return queryset

        return queryset.filter(
            state=MilestoneState.ACTIVE if value else MilestoneState.CLOSED,
        )


class MilestonesFilterSet(django_filters.FilterSet):
    """Set of filters for Milestone."""

    class Meta:
        model = Milestone
        fields = ("active", "state")

    active = ActiveFilter()
    q = SearchFilter(fields=("title", "=gl_url"))  # noqa: WPS111
    order_by = OrderingFilter(fields=("due_date",))
