# -*- coding: utf-8 -*-

import graphene

from .work_item_team_metrics import (
    IssueTeamMetricsType,
    MergeRequestTeamMetricsType,
)


class TeamMetricsType(graphene.ObjectType):
    """
    A class representing team metrics fields.
    """
    problems_count = graphene.Int()
    issues = graphene.Field(IssueTeamMetricsType)
    merge_requests = graphene.Field(MergeRequestTeamMetricsType)
