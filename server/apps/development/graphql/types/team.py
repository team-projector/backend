# -*- coding: utf-8 -*-

import graphene
from django.db.models import QuerySet
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.connections import DataSourceConnection
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode
from jnt_django_graphene_toolbox.types import BaseDjangoObjectType

from apps.development.graphql.filters import TeamMembersFilterSet
from apps.development.graphql.types.team_member import TeamMemberType
from apps.development.graphql.types.team_metrics import TeamMetricsType
from apps.development.models import Team
from apps.development.services.team.allowed import filter_allowed_for_user
from apps.development.services.team.metrics.main import get_team_metrics


class TeamType(BaseDjangoObjectType):
    """Team type."""

    class Meta:
        model = Team
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
        name = "Team"

    metrics = graphene.Field(TeamMetricsType)
    members = DataSourceConnectionField(
        TeamMemberType,
        filterset_class=TeamMembersFilterSet,
    )

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get teams."""
        return filter_allowed_for_user(queryset, info.context.user)

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get team metrics."""
        return get_team_metrics(self)

    def resolve_members(self, info, **kwargs):  # noqa: WPS110
        """Get team members."""
        return self.teammember_set
