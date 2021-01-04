import graphene

from apps.development.graphql.types import GitlabServiceStatusType


class GitlabStatusType(graphene.ObjectType):
    """Gitlab status type."""

    services = graphene.List(GitlabServiceStatusType)
    last_issues = graphene.List("apps.development.graphql.types.IssueType")
    last_sync = graphene.DateTime()
