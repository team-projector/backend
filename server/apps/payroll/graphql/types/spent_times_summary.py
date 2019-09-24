# -*- coding: utf-8 -*-

import graphene


class IssuesSpentTimesSummaryType(graphene.ObjectType):
    spent = graphene.Int()
    closed_spent = graphene.Int()
    opened_spent = graphene.Int()


class MergeRequestsSpentTimesSummaryType(graphene.ObjectType):
    spent = graphene.Int()
    closed_spent = graphene.Int()
    opened_spent = graphene.Int()
    merged_spent = graphene.Int()


class SpentTimesSummaryType(graphene.ObjectType):
    spent = graphene.Int()
    opened_spent = graphene.Int()
    issues = graphene.Field(IssuesSpentTimesSummaryType)
    merge_requests = graphene.Field(MergeRequestsSpentTimesSummaryType)
