import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.payroll.graphql.filters import SalaryFilterSet
from apps.payroll.graphql.types import SalaryType


class SalariesQueries(graphene.ObjectType):
    """Class represents list of available fields for salary queries."""

    salary = DatasourceRelayNode.Field(SalaryType)
    all_salaries = DataSourceConnectionField(
        SalaryType,
        filterset_class=SalaryFilterSet,
    )
