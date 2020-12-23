from datetime import datetime, timedelta

import pytest
from django.db.models import Sum
from jnt_django_toolbox.helpers.date import begin_of_week
from jnt_django_toolbox.helpers.time import seconds

from apps.core.services.week import get_first_week_day
from apps.development.models.issue import IssueState
from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
)
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_weeks import (  # noqa: E501
    checkers,
)

KEY_TIME_SPENT = "time_spent"
KEY_SPENT = "spent"
METRICS_GROUP_WEEK = "week"


@pytest.fixture()
def issue(team_developer):
    """Create issue."""
    return IssueFactory.create(user=team_developer, due_date=datetime.now())


def test_simple(team, team_developer, team_leader, issue):
    """
    Test simple.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    monday = begin_of_week(datetime.now().date(), get_first_week_day())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum(KEY_TIME_SPENT),
    )[KEY_SPENT]
    issue.state = IssueState.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    metrics = get_progress_metrics(
        team,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        METRICS_GROUP_WEEK,
    )

    assert len(metrics) == 2

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == 2

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_many_weeks(team, team_developer, issue):
    """
    Test many weeks.

    :param team:
    :param team_developer:
    """
    monday = begin_of_week(datetime.now().date(), get_first_week_day())

    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=4),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=2, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum(KEY_TIME_SPENT),
    )[KEY_SPENT]
    issue.due_date = monday + timedelta(days=2)
    issue.save()

    metrics = get_progress_metrics(
        team,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        METRICS_GROUP_WEEK,
    )

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == 2

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={
            monday - timedelta(weeks=1): timedelta(hours=5),
            monday: timedelta(hours=1),
        },
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_not_in_range(team, team_developer, issue):
    """
    Test not in range.

    :param team:
    :param team_developer:
    """
    monday = begin_of_week(datetime.now().date(), get_first_week_day())

    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=4),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=2, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum(KEY_TIME_SPENT),
    )[KEY_SPENT]
    issue.state = IssueState.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    metrics = get_progress_metrics(
        team,
        monday,
        monday + timedelta(weeks=1, days=5),
        METRICS_GROUP_WEEK,
    )

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == 2

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={monday: timedelta(hours=1)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_another_user(team, team_developer, another_user, issue):
    """
    Test another user.

    :param team:
    :param team_developer:
    """
    monday = begin_of_week(datetime.now().date(), get_first_week_day())

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=another_user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum(KEY_TIME_SPENT),
    )[KEY_SPENT]
    issue.state = IssueState.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, METRICS_GROUP_WEEK)

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == 2

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={monday: timedelta(hours=5)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_many_issues(team, team_developer, issue):
    """
    Test many issues.

    :param team:
    :param team_developer:
    """
    monday = begin_of_week(datetime.now().date())
    another_issue = IssueFactory.create(
        user=team_developer,
        due_date=monday + timedelta(days=4),
        total_time_spent=timedelta(hours=3).total_seconds(),
        time_estimate=timedelta(hours=10).total_seconds(),
    )

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=team_developer,
        base=another_issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=team_developer,
        base=another_issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum(KEY_TIME_SPENT),
    )[KEY_SPENT]
    issue.state = IssueState.OPENED
    issue.due_date = monday + timedelta(days=1)
    issue.save()

    another_issue.total_time_spent = another_issue.time_spents.aggregate(
        spent=Sum(KEY_TIME_SPENT),
    )[KEY_SPENT]
    another_issue.save()

    metrics = get_progress_metrics(
        team,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        METRICS_GROUP_WEEK,
    )

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == 2

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 2},
        time_estimates={monday: timedelta(days=1, hours=1)},
    )
