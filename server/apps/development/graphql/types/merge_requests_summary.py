# -*- coding: utf-8 -*-

import graphene
from jnt_django_graphene_toolbox.security.mixins.node import AuthNode
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated


class MergeRequestsSummaryType(AuthNode, graphene.ObjectType):
    """Merge requests summary type."""

    permission_classes = (AllowAuthenticated,)

    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    merged_count = graphene.Int()
