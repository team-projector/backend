import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.development.graphql.fields import AllIssuesConnectionField
from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.graphql.types import IssuesSummaryType, IssueType


class IssuesQueries(graphene.ObjectType):
    """Class represents list of available fields for issue queries."""

    issue = ModelRelayNode.Field(IssueType)
    all_issues = AllIssuesConnectionField()
    issues_summary = graphene.Field(
        IssuesSummaryType,
        resolver=resolve_issues_summary,
        due_date=graphene.Date(),
        user=graphene.ID(),
        team=graphene.ID(),
        state=graphene.String(),
        problems=graphene.Boolean(),
        project=graphene.ID(),
        milestone=graphene.ID(),
        ticket=graphene.ID(),
    )
