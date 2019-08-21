import graphene

from apps.development.graphql.resolvers.issues_summary import (
    resolve_issues_project_summaries
)
from .issues_project_summary import IssuesProjectSummary


class IssuesSummaryType(graphene.ObjectType):
    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    time_spent = graphene.Int()
    problems_count = graphene.Int()
    projects = graphene.List(IssuesProjectSummary,
                             order_by=graphene.String(),
                             resolver=resolve_issues_project_summaries)
