import graphene
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.payroll.graphql.fields import WorkBreaksConnectionField
from apps.payroll.graphql.types import WorkBreakType


class WorkBreaksQueries(graphene.ObjectType):
    """Class represents list of available fields for work break queries."""

    work_break = DatasourceRelayNode.Field(WorkBreakType)
    all_work_breaks = WorkBreaksConnectionField()
