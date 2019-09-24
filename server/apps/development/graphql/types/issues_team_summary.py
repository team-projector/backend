# -*- coding: utf-8 -*-

import graphene

from .team import TeamType
from .project_issues_summary import ProjectIssuesSummary


class IssuesTeamSummary(graphene.ObjectType):
    team = graphene.Field(TeamType)
    issues = graphene.Field(ProjectIssuesSummary)
