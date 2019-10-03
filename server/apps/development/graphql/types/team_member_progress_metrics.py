# -*- coding: utf-8 -*-

import graphene

from apps.users.graphql.types import UserProgressMetricsType, UserType


class TeamMemberProgressMetricsType(graphene.ObjectType):
    """
    A class representing team member progress metrics fields.
    """
    user = graphene.Field(UserType)
    metrics = graphene.List(UserProgressMetricsType)
