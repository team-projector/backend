import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.payroll.graphql.filters import WorkBreakFilterSet
from apps.payroll.graphql.types import WorkBreakType


class WorkBreaksQueries(graphene.ObjectType):
    work_break = DatasourceRelayNode.Field(WorkBreakType)
    all_work_breaks = DataSourceConnectionField(
        WorkBreakType,
        filterset_class=WorkBreakFilterSet
    )
