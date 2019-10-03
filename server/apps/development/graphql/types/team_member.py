# -*- coding: utf-8 -*-

from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.development.models import TeamMember
from apps.users.graphql.types import UserType


class TeamMemberType(UserType):
    """
    A class representing Team Member model.
    """
    class Meta:
        model = TeamMember
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'TeamMember'
