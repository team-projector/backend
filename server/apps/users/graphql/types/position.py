from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.users.models import Position


class PositionType(BaseDjangoObjectType):
    """Position type."""

    class Meta:
        model = Position
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Position"
