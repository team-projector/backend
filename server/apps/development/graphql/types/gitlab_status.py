import graphene

from apps.development.graphql.types.gitlab_service_status import (
    GitlabServiceStatusType,
)
from apps.development.graphql.types.issue import IssueType


class GitlabStatusType(graphene.ObjectType):
    """Gitlab status type."""

    services = graphene.List(GitlabServiceStatusType)
    last_issues = graphene.List(IssueType)
    last_sync = graphene.DateTime()
