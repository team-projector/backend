from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.payroll.models import WorkBreak


class WorkBreakType(BaseDjangoObjectType):
    class Meta:
        model = WorkBreak
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'WorkBreak'

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = WorkBreak.objects.allowed_for_user(
            info.context.user
        )

        return queryset
