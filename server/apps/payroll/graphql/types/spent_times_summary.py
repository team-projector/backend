# -*- coding: utf-8 -*-

import graphene


class IssuesSpentTimesSummaryType(graphene.ObjectType):
    """
    A class representing issues fields for summary spent time.
    """
    spent = graphene.Int()
    closed_spent = graphene.Int()
    opened_spent = graphene.Int()


class MergeRequestsSpentTimesSummaryType(graphene.ObjectType):
    """
    A class representing merge requests fields for summary spent time.
    """
    spent = graphene.Int()
    closed_spent = graphene.Int()
    opened_spent = graphene.Int()
    merged_spent = graphene.Int()


class SpentTimesSummaryType(graphene.ObjectType):
    """
    A class representing summaries fields of spent time.
    """
    spent = graphene.Int()
    opened_spent = graphene.Int()
    issues = graphene.Field(IssuesSpentTimesSummaryType)
    merge_requests = graphene.Field(MergeRequestsSpentTimesSummaryType)
