import graphene

from .issues_project_summary import IssuesProjectSummary


class IssuesSummaryType(graphene.ObjectType):
    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    time_spent = graphene.Int()
    problems_count = graphene.Int()
    projects = graphene.List(IssuesProjectSummary)
