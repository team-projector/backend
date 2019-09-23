import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.payroll.graphql.filters import SalaryFilterSet
from apps.payroll.graphql.types import SalaryType


class SalariesQueries(graphene.ObjectType):
    salary = DatasourceRelayNode.Field(SalaryType)
    all_salaries = DataSourceConnectionField(
        SalaryType,
        filterset_class=SalaryFilterSet,
    )
