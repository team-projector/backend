# -*- coding: utf-8 -*-

import graphene


class WorkItemTeamMetricsType(graphene.ObjectType):
    """Work item team metrics type."""
    count = graphene.Int()
    opened_count = graphene.Int()
    opened_estimated = graphene.Int()


class IssueTeamMetricsType(WorkItemTeamMetricsType):
    """Issue team metrics type."""


class MergeRequestTeamMetricsType(WorkItemTeamMetricsType):
    """Merge request team metrics type."""
