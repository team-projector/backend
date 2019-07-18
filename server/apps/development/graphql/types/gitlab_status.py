import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from .gitlab_service_status import GitlabServiceStatusType
from .issue import IssueType


class GitlabStatusType(graphene.ObjectType):
    services = graphene.List(GitlabServiceStatusType)
    last_issues = DataSourceConnectionField(IssueType)
    last_sync = graphene.DateTime()
