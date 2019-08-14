from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Feature


class FeatureType(BaseDjangoObjectType):
    class Meta:
        model = Feature
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Feature'
