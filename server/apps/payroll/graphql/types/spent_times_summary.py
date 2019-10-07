# -*- coding: utf-8 -*-

import graphene


class IssuesSpentTimesSummaryType(graphene.ObjectType):
    """Issues spent time summary type."""

    spent = graphene.Int()
    closed_spent = graphene.Int()
    opened_spent = graphene.Int()


class MergeRequestsSpentTimesSummaryType(graphene.ObjectType):
    """Merge requests spent times summary type."""

    spent = graphene.Int()
    closed_spent = graphene.Int()
    opened_spent = graphene.Int()
    merged_spent = graphene.Int()


class SpentTimesSummaryType(graphene.ObjectType):
    """Spent times summary type."""

    spent = graphene.Int()
    opened_spent = graphene.Int()
    issues = graphene.Field(IssuesSpentTimesSummaryType)
    merge_requests = graphene.Field(MergeRequestsSpentTimesSummaryType)
