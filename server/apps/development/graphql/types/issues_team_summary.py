# -*- coding: utf-8 -*-

import graphene

from apps.development.graphql.types.project_issues_summary import (
    ProjectIssuesSummary,
)
from apps.development.graphql.types.team import TeamType


class IssuesTeamSummary(graphene.ObjectType):
    """Issues team summary."""

    team = graphene.Field(TeamType)
    issues = graphene.Field(ProjectIssuesSummary)
