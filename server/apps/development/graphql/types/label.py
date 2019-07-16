from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.models import Label


class LabelType(DjangoObjectType):
    class Meta:
        model = Label
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        filter_fields: list = []
        name = 'Label'
