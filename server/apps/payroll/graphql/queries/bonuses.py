import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.payroll.graphql.fields import AllBonusesConnectionField
from apps.payroll.graphql.types import BonusType


class BonusesQueries(graphene.ObjectType):
    """Class represents list of available fields for bonuses queries."""

    bonus = ModelRelayNode.Field(BonusType)
    all_bonuses = AllBonusesConnectionField()
