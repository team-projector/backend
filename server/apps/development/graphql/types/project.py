from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Project


class ProjectType(BaseDjangoObjectType):
    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Project'
