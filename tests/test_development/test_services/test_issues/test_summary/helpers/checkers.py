# -*- coding: utf-8 -*-

from apps.development.models import Project, Team
from apps.development.services.issue.summary.issue import IssuesSummary


def check_summary(  # noqa: WPS211
    summary: IssuesSummary,
    count: int = 0,
    opened_count: int = 0,
    closed_count: int = 0,
    time_spent: int = 0,
    problems_count: int = 0,
):
    """Check issue summary."""
    assert summary.count == count
    assert summary.opened_count == opened_count
    assert summary.closed_count == closed_count
    assert summary.time_spent == time_spent
    assert summary.problems_count == problems_count


def check_project_stats(
    summary: IssuesSummary,
    project: Project,
    issues_opened_count: int = 0,
    percentage: float = 0,
    remains: int = 0,
):
    """Check projects stats."""
    stats = next(
        (
            project_stats
            for project_stats in summary.projects
            if project_stats.project == project
        ),
        None,
    )

    assert stats is not None
    assert stats.issues.opened_count == issues_opened_count
    assert stats.issues.percentage == percentage
    assert stats.issues.remains == remains


def check_team_stats(
    summary: IssuesSummary,
    team: Team,
    issues_opened_count: int = 0,
    percentage: float = 0,
    remains: int = 0,
):
    """Check teams stats."""
    stats = next(
        (
            team_stats
            for team_stats in summary.teams
            if team_stats.team == team
        ),
        None,
    )

    assert stats is not None
    assert stats.issues.opened_count == issues_opened_count
    assert stats.issues.percentage == percentage
    assert stats.issues.remains == remains
