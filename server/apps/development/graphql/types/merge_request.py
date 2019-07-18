from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.types.interfaces import SpentTimeBase
from apps.development.models import MergeRequest


class MergeRequestType(BaseDjangoObjectType):
    class Meta:
        model = MergeRequest
        interfaces = (DatasourceRelayNode, SpentTimeBase)
        connection_class = DataSourceConnection
        name = 'MergeRequest'
