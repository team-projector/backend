# -*- coding: utf-8 -*-

import graphene

from apps.users.graphql.types import UserType, UserProgressMetricsType


class TeamMemberProgressMetricsType(graphene.ObjectType):
    user = graphene.Field(UserType)
    metrics = graphene.List(UserProgressMetricsType)
