from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.users.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude_fields = ('password',)
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
