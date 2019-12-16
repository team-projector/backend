# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql import DatasourceRelayNode
from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.ticket_metrics import TicketMetricsType
from apps.development.models import Ticket
from apps.development.services.ticket import allowed, metrics


class TicketType(BaseDjangoObjectType):
    """Class representing list of available fields for ticket queries."""

    metrics = graphene.Field(TicketMetricsType)
    type = graphene.String()  # noqa: A003

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get metrics."""
        allowed.check_project_manager(info.context.user)
        return metrics.get_ticket_metrics(self)

    class Meta:
        model = Ticket
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Ticket'

    @classmethod
    def get_queryset(
        cls,
        queryset,
        info,  # noqa: WPS110
    ) -> QuerySet:
        """Get tickets."""
        return queryset
