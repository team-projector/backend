# -*- coding: utf-8 -*-

from apps.development.models import Project, Team
from apps.development.services.issue.summary.issue import IssuesSummary


def check_summary(
    summary: IssuesSummary,
    count: int = 0,
    opened_count: int = 0,
    closed_count: int = 0,
    time_spent: int = 0,
    problems_count: int = 0,
):
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
    stats = next(
        (item for item in summary.projects if item.project == project), None,
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
    stats = next((item for item in summary.teams if item.team == team), None)

    assert stats is not None
    assert stats.issues.opened_count == issues_opened_count
    assert stats.issues.percentage == percentage
    assert stats.issues.remains == remains
