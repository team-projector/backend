# -*- coding: utf-8 -*-

import graphene


class WorkItemUserMetricsType(graphene.ObjectType):
    """
    Work item user metrics type.
    """
    opened_count = graphene.Int()
    closed_spent = graphene.Float()
    opened_spent = graphene.Float()


class IssueUserMetricsType(WorkItemUserMetricsType):
    """
    Issue user metrics type.
    """
    pass


class MergeRequestUserMetricsType(WorkItemUserMetricsType):
    """
    Merge request user metrics type.
    """
    pass
