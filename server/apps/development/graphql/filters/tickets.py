# -*- coding: utf-8 -*-

import django_filters

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import Milestone, Ticket


class TicketsFilterSet(django_filters.FilterSet):
    """Set of filters for Ticket."""

    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all(),
    )
    order_by = OrderingFilter(
        fields=("due_date", "title"),
    )

    class Meta:
        model = Ticket
        fields = ("milestone",)
