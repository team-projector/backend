import graphene

from apps.development.graphql.types.work_item_team_metrics import (
    IssueTeamMetricsType,
    MergeRequestTeamMetricsType,
)


class TeamMetricsType(graphene.ObjectType):
    """Team metrics type."""

    problems_count = graphene.Int()
    issues = graphene.Field(IssueTeamMetricsType)
    merge_requests = graphene.Field(MergeRequestTeamMetricsType)
