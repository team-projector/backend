import graphene

from apps.development.graphql.fields.all_teams import TeamSort
from apps.development.graphql.resolvers.issues_summary import (
    resolve_issues_project_summaries,
    resolve_issues_team_summaries,
)
from apps.development.graphql.types.issues_project_summary import (
    IssuesProjectSummary,
)
from apps.development.graphql.types.issues_team_summary import (
    IssuesTeamSummary,
)
from apps.development.models.project import ProjectState


class IssueSummaryProjectSort(graphene.Enum):
    """Allowed sort fields."""

    ISSUES_REMAINS_ASC = "issues__remains"  # noqa: WPS115
    ISSUES_REMAINS_DESC = "-issues__remains"  # noqa: WPS115


class IssuesSummaryType(graphene.ObjectType):
    """Issues summary type."""

    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    time_spent = graphene.Int()
    problems_count = graphene.Int()
    projects = graphene.List(
        IssuesProjectSummary,
        order_by=graphene.Argument(graphene.List(IssueSummaryProjectSort)),
        state=graphene.Argument(
            graphene.Enum.from_enum(ProjectState),
        ),
        resolver=resolve_issues_project_summaries,
    )
    teams = graphene.List(
        IssuesTeamSummary,
        order_by=graphene.Argument(graphene.List(TeamSort)),
        resolver=resolve_issues_team_summaries,
    )
