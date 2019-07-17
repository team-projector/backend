import graphene

from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.payroll.graphql.filters import SalaryFilterSet
from apps.payroll.graphql.types import SalaryType


class SalariesQueries(graphene.ObjectType):
    salary = DatasourceRelayNode.Field(SalaryType)
    all_salaries = DataSourceConnectionField(
        SalaryType,
        filterset_class=SalaryFilterSet
    )
