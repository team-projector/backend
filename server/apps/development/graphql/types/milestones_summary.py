# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.security.mixins.node import AuthNode
from apps.core.graphql.security.permissions import AllowAuthenticated


class MilestonesSummaryType(AuthNode, graphene.ObjectType):
    """Milestones summary type."""

    permission_classes = (AllowAuthenticated,)

    count = graphene.Int()
    active_count = graphene.Int()
    closed_count = graphene.Int()
