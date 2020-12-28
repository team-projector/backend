import graphene
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.graphql.fields import (
    TeamsConnectionField,
    TeamWorkBreaksConnectionField,
)
from apps.development.graphql.resolvers import resolve_team_progress_metrics
from apps.development.graphql.types import (
    TeamMemberProgressMetricsType,
    TeamType,
)


class TeamsQueries(graphene.ObjectType):
    """Class represents list of available fields for team queries."""

    team = DatasourceRelayNode.Field(TeamType)
    all_teams = TeamsConnectionField()
    team_progress_metrics = graphene.Field(
        graphene.List(TeamMemberProgressMetricsType),
        resolver=resolve_team_progress_metrics,
        team=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
        group=graphene.String(required=True),
    )
    team_work_breaks = TeamWorkBreaksConnectionField()
