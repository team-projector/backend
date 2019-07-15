from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.models import MergeRequest
from apps.development.graphql.types.interfaces import SpentTimeBase


class MergeRequestType(DjangoObjectType):
    class Meta:
        model = MergeRequest
        interfaces = (DatasourceRelayNode, SpentTimeBase)
        connection_class = DataSourceConnection
        name = 'MergeRequest'
