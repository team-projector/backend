import graphene
from jnt_django_graphene_toolbox.nodes import ModelRelayNode

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
        team=graphene.ID(),
        state=graphene.String(),
        problems=graphene.Boolean(),
        project=graphene.ID(),
        milestone=graphene.ID(),
        ticket=graphene.ID(),
        participated_by=graphene.ID(),
        created_by=graphene.ID(),
        assigned_to=graphene.ID(),
        created_by_for_other=graphene.ID(),
    )
