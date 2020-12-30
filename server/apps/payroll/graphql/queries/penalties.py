import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.payroll.graphql.fields import AllPenaltiesConnectionField
from apps.payroll.graphql.types import PenaltyType


class PenaltiesQueries(graphene.ObjectType):
    """Class represents list of available fields for penalty queries."""

    penalty = ModelRelayNode.Field(PenaltyType)
    all_penalties = AllPenaltiesConnectionField()
