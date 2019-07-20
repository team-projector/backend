import graphene

from .project import ProjectType
from .project_issues_summary import ProjectIssuesSummary


class IssuesProjectSummary(graphene.ObjectType):
    project = graphene.Field(ProjectType)
    issues = graphene.Field(ProjectIssuesSummary)
