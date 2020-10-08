import graphene

from apps.users.graphql.types import UserProgressMetricsType, UserType


class TeamMemberProgressMetricsType(graphene.ObjectType):
    """Team member progress metrics type."""

    user = graphene.Field(UserType)
    metrics = graphene.List(UserProgressMetricsType)
