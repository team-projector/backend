# -*- coding: utf-8 -*-

import graphene
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.users.graphql.resolvers import (
    resolve_me_user,
    resolve_user_progress_metrics,
)
from apps.users.graphql.types import UserProgressMetricsType, UserType


class UsersQueries(graphene.ObjectType):
    """Class representing list of available fields for user queries."""

    user = DatasourceRelayNode.Field(UserType)

    user_progress_metrics = graphene.Field(
        graphene.List(UserProgressMetricsType),
        user=graphene.ID(required=True),
        start=graphene.Date(required=True),
        end=graphene.Date(required=True),
        group=graphene.String(required=True),
        resolver=resolve_user_progress_metrics,
    )

    me = graphene.Field(UserType, resolver=resolve_me_user)
