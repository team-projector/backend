# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.security.mixins.node import AuthNode
from apps.core.graphql.security.permissions import AllowAuthenticated


class MergeRequestsSummaryType(
    AuthNode, graphene.ObjectType,
):
    """Merge requests summary type."""

    permission_classes = (AllowAuthenticated,)

    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    merged_count = graphene.Int()
