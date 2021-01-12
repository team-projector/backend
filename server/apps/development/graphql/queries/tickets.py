import graphene
from jnt_django_graphene_toolbox.nodes import ModelRelayNode

from apps.development.graphql.fields import AllTicketsConnectionField
from apps.development.graphql.resolvers.tickets_summary import (
    resolve_tickets_summary,
)
from apps.development.graphql.types import TicketsSummaryType, TicketType


class TicketsQueries(graphene.ObjectType):
    """Class represents list of available fields for ticket queries."""

    ticket = ModelRelayNode.Field(TicketType)
    all_tickets = AllTicketsConnectionField()
    tickets_summary = graphene.Field(
        TicketsSummaryType,
        milestone=graphene.ID(),
        resolver=resolve_tickets_summary,
    )
