import graphene

from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.filters import TeamsFilterSet
from apps.development.graphql.types import TeamType


class TeamsQueries(graphene.ObjectType):
    team = DatasourceRelayNode.Field(TeamType)
    all_teams = DataSourceConnectionField(
        TeamType,
        filterset_class=TeamsFilterSet
    )
