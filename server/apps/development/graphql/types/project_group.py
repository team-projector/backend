from graphene_django import DjangoObjectType

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.models import ProjectGroup
from apps.development.graphql.types.interfaces import Owner


class ProjectGroupType(DjangoObjectType):
    class Meta:
        model = ProjectGroup
        interfaces = (DatasourceRelayNode, Owner)
        connection_class = DataSourceConnection
        name = 'ProjectGroup'
