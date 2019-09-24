# -*- coding: utf-8 -*-

import graphene


class WorkItemUserMetricsType(graphene.ObjectType):
    opened_count = graphene.Int()
    closed_spent = graphene.Float()
    opened_spent = graphene.Float()


class IssueUserMetricsType(WorkItemUserMetricsType):
    pass


class MergeRequestUserMetricsType(WorkItemUserMetricsType):
    pass
