# -*- coding: utf-8 -*-

import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.graphql.filters import TeamsFilterSet
from apps.development.graphql.resolvers import resolve_team_progress_metrics
from apps.development.graphql.types import (
    TeamMemberProgressMetricsType,
    TeamType,
)


class TeamsQueries(graphene.ObjectType):
    """Class representing list of available fields for team queries."""

    team = DatasourceRelayNode.Field(TeamType)

    all_teams = DataSourceConnectionField(
        TeamType, filterset_class=TeamsFilterSet,
    )

    team_progress_metrics = graphene.Field(
        graphene.List(TeamMemberProgressMetricsType),
        team=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
        group=graphene.String(required=True),
        resolver=resolve_team_progress_metrics,
    )
