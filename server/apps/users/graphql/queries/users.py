import graphene
from jnt_django_graphene_toolbox.nodes import ModelRelayNode

from apps.users.graphql.fields import AllUsersConnectionField
from apps.users.graphql.resolvers import (
    resolve_me_user,
    resolve_user_progress_metrics,
    resolve_work_calendar,
)
from apps.users.graphql.types import (
    UserProgressMetricsType,
    UserType,
    WorkCalendarType,
)
from apps.users.services.user.metrics.progress.main import GroupProgressMetrics


class UsersQueries(graphene.ObjectType):
    """Class represents list of available fields for user queries."""

    user = ModelRelayNode.Field(UserType)
    all_users = AllUsersConnectionField()
    user_progress_metrics = graphene.Field(
        graphene.List(UserProgressMetricsType),
        resolver=resolve_user_progress_metrics,
        user=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
        group=graphene.Argument(
            graphene.Enum.from_enum(GroupProgressMetrics),
            required=True,
        ),
    )

    me = graphene.Field(UserType, resolver=resolve_me_user)
    work_calendar = graphene.Field(
        graphene.List(WorkCalendarType),
        resolver=resolve_work_calendar,
        user=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
    )
