# -*- coding: utf-8 -*-

import django_filters

from apps.core.graphql.filters.ordering import OrderingFilter
from apps.development.models import Milestone, Ticket
from apps.development.models.ticket import TicketState


class TicketsFilterSet(django_filters.FilterSet):
    """Set of filters for Ticket."""

    state = django_filters.ChoiceFilter(choices=TicketState.choices)

    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all(),
    )
    order_by = OrderingFilter(
        fields=("due_date", "start_date", "title"),
    )

    class Meta:
        model = Ticket
        fields = ("milestone", "state")
