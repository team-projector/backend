from datetime import datetime

from apps.development.models import Issue, Project
from apps.development.models.issue import STATE_CLOSED
from apps.development.services.summary.issues import (
    get_issues_summary, IssuesSummary
)
from tests.test_development.factories import (
    IssueFactory, ProjectFactory
)


def test_basic(user):
    project_1 = ProjectFactory()
    project_2 = ProjectFactory()

    IssueFactory.create_batch(
        5,
        user=user,
        total_time_spent=300,
        time_estimate=400,
        project=project_1,
        due_date=datetime.now().date()
    )

    IssueFactory.create_batch(
        2,
        user=user,
        state=STATE_CLOSED,
        total_time_spent=200,
        time_estimate=400,
        project=project_1,
        due_date=datetime.now().date()
    )

    IssueFactory.create_batch(
        3,
        user=user,
        total_time_spent=100,
        time_estimate=400,
        project=project_2,
        due_date=datetime.now().date()
    )

    summary = get_issues_summary(
        Issue.objects.all(),
        datetime.now().date(),
        user,
        None,
    )

    assert len(summary.projects) == 2
    _check_project_stats(
        summary,
        project_1,
        issues_opened_count=5,
        percentage=5 / 8,
        remains=500
    )

    _check_project_stats(
        summary,
        project_2,
        issues_opened_count=3,
        percentage=3 / 8,
        remains=900
    )


def _check_project_stats(data: IssuesSummary,
                         project: Project,
                         issues_opened_count: int,
                         percentage: float,
                         remains: int):
    stats = next((
        item
        for item in data.projects
        if item.project == project
    ), None)

    assert stats is not None
    assert stats.issues.opened_count == issues_opened_count
    assert stats.issues.percentage == percentage
    assert stats.issues.remains == remains
