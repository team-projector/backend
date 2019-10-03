# -*- coding: utf-8 -*-

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.models import Label


class LabelType(BaseDjangoObjectType):
    """
    A class representing Label model.
    """
    class Meta:
        model = Label
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        filter_fields: list = []
        name = 'Label'
