# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.graphql.filters import TicketsFilterSet
from apps.development.graphql.types import TicketType


class TicketsQueries(graphene.ObjectType):
    """Class representing list of available fields for ticket queries."""

    ticket = DatasourceRelayNode.Field(TicketType)

    all_tickets = DataSourceConnectionField(
        TicketType,
        filterset_class=TicketsFilterSet,
    )
