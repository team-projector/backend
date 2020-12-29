import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.payroll.graphql.fields import WorkBreaksConnectionField
from apps.payroll.graphql.types import WorkBreakType


class WorkBreaksQueries(graphene.ObjectType):
    """Class represents list of available fields for work break queries."""

    work_break = ModelRelayNode.Field(WorkBreakType)
    all_work_breaks = WorkBreaksConnectionField()
