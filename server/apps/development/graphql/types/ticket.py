# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.ticket_metrics import TicketMetricsType
from apps.development.models import Ticket
from apps.development.services.allowed.ticket import check_project_manager
from apps.development.services.metrics.ticket import get_ticket_metrics


class TicketType(BaseDjangoObjectType):
    metrics = graphene.Field(TicketMetricsType)

    def resolve_metrics(self, info, **kwargs):
        check_project_manager(info.context.user)

        return get_ticket_metrics(self)

    class Meta:
        model = Ticket
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Ticket'

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        return queryset
