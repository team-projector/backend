# -*- coding: utf-8 -*-

import graphene


class MilestonesSummaryType(graphene.ObjectType):
    """Milestones summary type."""

    count = graphene.Int()
    active_count = graphene.Int()
    closed_count = graphene.Int()
