# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.core.graphql.connections import DataSourceConnection
from apps.core.graphql.relay_nodes import DatasourceRelayNode
from apps.core.graphql.types import BaseDjangoObjectType
from apps.development.graphql.filters import TeamMembersFilterSet
from apps.development.graphql.types.team_member import TeamMemberType
from apps.development.graphql.types.team_metrics import TeamMetricsType
from apps.development.models import Team
from apps.development.services import team as team_service


class TeamType(BaseDjangoObjectType):
    """Team type."""

    metrics = graphene.Field(TeamMetricsType)
    members = DataSourceConnectionField(
        TeamMemberType,
        filterset_class=TeamMembersFilterSet,
    )

    class Meta:
        model = Team
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = 'Team'

    @classmethod
    def get_queryset(
        cls,
        queryset,
        info,  # noqa WPS110
    ) -> QuerySet:
        """Get teams."""
        queryset = team_service.filter_allowed_for_user(
            queryset,
            info.context.user,
        )

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa WPS110
        """Get team metrics."""
        return team_service.get_metrics(self)

    def resolve_members(self, info, **kwargs):  # noqa WPS110
        """Get team members."""
        return self.teammember_set
