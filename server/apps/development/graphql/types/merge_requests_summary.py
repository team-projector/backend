# -*- coding: utf-8 -*-

import graphene


class MergeRequestsSummaryType(graphene.ObjectType):
    """
    A class representing merge requests summary fields.
    """
    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    merged_count = graphene.Int()
