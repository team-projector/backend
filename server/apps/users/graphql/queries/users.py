import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.users.graphql.fields import UsersConnectionField
from apps.users.graphql.resolvers import (
    resolve_me_user,
    resolve_user_progress_metrics,
)
from apps.users.graphql.types import UserProgressMetricsType, UserType


class UsersQueries(graphene.ObjectType):
    """Class represents list of available fields for user queries."""

    user = ModelRelayNode.Field(UserType)
    all_users = UsersConnectionField()

    user_progress_metrics = graphene.Field(
        graphene.List(UserProgressMetricsType),
        resolver=resolve_user_progress_metrics,
        user=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
        group=graphene.String(required=True),
    )

    me = graphene.Field(UserType, resolver=resolve_me_user)
