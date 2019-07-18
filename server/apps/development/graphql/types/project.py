from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Project
from apps.development.graphql.types.interfaces import BaseWorkItem


class ProjectType(BaseDjangoObjectType):
    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode, BaseWorkItem)
        connection_class = DataSourceConnection
        name = 'Project'
