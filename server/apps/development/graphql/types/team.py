import graphene
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.filters import TeamMembersFilterSet
from apps.development.models import Team
from apps.development.services.allowed.teams import filter_allowed_for_user
from apps.development.services.metrics.team import get_team_metrics
from .team_member import TeamMemberType
from .team_metrics import TeamMetricsType


class TeamType(DjangoObjectType):
    metrics = graphene.Field(TeamMetricsType)
    members = DataSourceConnectionField(
        TeamMemberType,
        filterset_class=TeamMembersFilterSet
    )

    class Meta:
        model = Team
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Team'

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        queryset = filter_allowed_for_user(
            queryset,
            info.context.user
        )

        return queryset

    def resolve_metrics(self, info, **kwargs):
        return get_team_metrics(self)

    def resolve_members(self, info, **kwargs):
        return self.teammember_set