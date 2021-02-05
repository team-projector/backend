import graphene

from apps.development.graphql.types import IssueType
from apps.users.graphql.types import UserProgressMetricsType


class WorkCalendarType(graphene.ObjectType):
    """Work calendar type."""

    date = graphene.Date()
    metrics = graphene.Field(UserProgressMetricsType)
    issues = graphene.List(IssueType)
