from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.models import TeamMember
from apps.users.graphql.types import UserType


class TeamMemberType(UserType):
    class Meta:
        model = TeamMember
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'TeamMember'
