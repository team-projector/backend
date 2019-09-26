# -*- coding: utf-8 -*-

import graphene

from .project_issues_summary import ProjectIssuesSummary
from .team import TeamType


class IssuesTeamSummary(graphene.ObjectType):
    team = graphene.Field(TeamType)
    issues = graphene.Field(ProjectIssuesSummary)
