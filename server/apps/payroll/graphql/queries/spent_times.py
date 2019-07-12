import graphene

from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.graphql.types import SpentTimeType


class TimeExpensesQueries(graphene.ObjectType):
    all_spent_times = DataSourceConnectionField(
        SpentTimeType,
        filterset_class=SpentTimeFilterSet
    )
