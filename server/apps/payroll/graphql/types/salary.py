import graphene
from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.interfaces import WorkItem
from apps.payroll.models import Salary
from apps.payroll.services.allowed.salary import filter_allowed_for_user


class SalaryType(BaseDjangoObjectType):
    owner = graphene.Field(WorkItem)

    class Meta:
        model = Salary
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Salary'

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        return filter_allowed_for_user(
            queryset,
            info.context.user
        )
