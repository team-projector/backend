# -*- coding: utf-8 -*-

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.users.models import Position


class PositionType(BaseDjangoObjectType):
    """Position type."""

    class Meta:
        model = Position
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Position"
