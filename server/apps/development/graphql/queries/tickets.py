# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.graphql.filters import TicketsFilterSet
from apps.development.graphql.resolvers.tickets_summary import (
    resolve_tickets_summary,
)
from apps.development.graphql.types import TicketsSummaryType, TicketType


class TicketsQueries(graphene.ObjectType):
    """Class representing list of available fields for ticket queries."""

    ticket = DatasourceRelayNode.Field(TicketType)

    all_tickets = DataSourceConnectionField(
        TicketType, filterset_class=TicketsFilterSet,
    )

    tickets_summary = graphene.Field(
        TicketsSummaryType,
        milestone=graphene.ID(),
        resolver=resolve_tickets_summary,
    )
