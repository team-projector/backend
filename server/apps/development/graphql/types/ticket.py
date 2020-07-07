# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.core import graphql
from apps.development.graphql.types.ticket_metrics import TicketMetricsType
from apps.development.models import Ticket
from apps.development.services.ticket import allowed, metrics
from apps.development.services.ticket.problems import (
    annotate_ticket_problems,
    get_ticket_problems,
)


class TicketType(BaseDjangoObjectType):
    """Class representing list of available fields for ticket queries."""

    class Meta:
        model = Ticket
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Ticket"

    metrics = graphene.Field(TicketMetricsType)
    type = graphene.String()  # noqa: WPS125
    problems = graphene.List(graphene.String)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get tickets."""
        if graphql.is_field_selected(info, "edges.node.problems"):
            queryset = annotate_ticket_problems(queryset)

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get metrics."""
        allowed.check_project_manager(info.context.user)
        return metrics.get_ticket_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get ticket problems."""
        return get_ticket_problems(self)
