# -*- coding: utf-8 -*-

import graphene

from apps.users.graphql.types import UserProgressMetricsType, UserType


class TeamMemberProgressMetricsType(graphene.ObjectType):
    user = graphene.Field(UserType)
    metrics = graphene.List(UserProgressMetricsType)
