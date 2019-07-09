from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.models import Project


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
