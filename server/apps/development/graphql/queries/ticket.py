# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.filters import TicketsFilterSet
from apps.development.graphql.types import TicketType


class TicketsQueries(graphene.ObjectType):
    all_tickets = DataSourceConnectionField(
        TicketType,
        filterset_class=TicketsFilterSet,
    )
