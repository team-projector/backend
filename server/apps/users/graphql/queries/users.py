import graphene

from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.users.graphql.resolvers import (
    resolve_me_user,
    resolve_user_progress_metrics
)
from apps.users.graphql.types import UserType, UserProgressMetricsType


class UsersQueries(graphene.ObjectType):
    user = DatasourceRelayNode.Field(UserType)
    user_progress_metrics = graphene.Field(
        graphene.List(UserProgressMetricsType),
        user=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
        group=graphene.String(required=True),
        resolver=resolve_user_progress_metrics
    )
    me_user = graphene.Field(
        UserType,
        resolver=resolve_me_user
    )
