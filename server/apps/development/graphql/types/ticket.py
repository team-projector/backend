from django.db.models import QuerySet

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Ticket
from apps.development.services.allowed.ticket import filter_allowed_for_user


class TicketType(BaseDjangoObjectType):
    class Meta:
        model = Ticket
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Ticket'

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user
        )

        return queryset
