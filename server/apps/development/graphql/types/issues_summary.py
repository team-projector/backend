# -*- coding: utf-8 -*-

import graphene

from apps.development.graphql.resolvers.issues_summary import (
    resolve_issues_project_summaries,
    resolve_issues_team_summaries,
)
from apps.development.graphql.types.issues_project_summary import (
    IssuesProjectSummary,
)
from apps.development.graphql.types.issues_team_summary import (
    IssuesTeamSummary,
)


class IssuesSummaryType(graphene.ObjectType):
    """Issues summary type."""

    count = graphene.Int()
    opened_count = graphene.Int()
    closed_count = graphene.Int()
    time_spent = graphene.Int()
    problems_count = graphene.Int()
    projects = graphene.List(
        IssuesProjectSummary,
        order_by=graphene.String(),
        is_archived=graphene.Boolean(),
        resolver=resolve_issues_project_summaries,
    )
    teams = graphene.List(
        IssuesTeamSummary,
        order_by=graphene.String(),
        resolver=resolve_issues_team_summaries,
    )
