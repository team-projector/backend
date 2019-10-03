# -*- coding: utf-8 -*-

import graphene


class WorkItemTeamMetricsType(graphene.ObjectType):
    """
    A class representing work item fields.
    """
    count = graphene.Int()
    opened_count = graphene.Int()
    opened_estimated = graphene.Int()


class IssueTeamMetricsType(WorkItemTeamMetricsType):
    """
    A class representing issue fields.
    """
    pass


class MergeRequestTeamMetricsType(WorkItemTeamMetricsType):
    """
    A class representing merge request fields.
    """
    pass
