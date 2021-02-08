from datetime import datetime, timedelta

import pytest
from django.db.models import Sum
from django.utils import timezone
from jnt_django_toolbox.helpers.time import seconds

from apps.development.services.team.metrics.progress import (
    get_progress_metrics,
)
from apps.users.services.user.metrics.progress.main import GroupProgressMetrics
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_days import (  # noqa: E501
    checkers,
)


@pytest.fixture()
def issue(team_developer):
    """Create issue."""
    return IssueFactory.create(user=team_developer, due_date=datetime.now())


def test_simple(team, team_developer, team_leader):
    """
    Test simple.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    issue = IssueFactory.create(
        user=team_developer,
        time_estimate=seconds(hours=15),
        due_date=timezone.now() + timedelta(days=1),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == 2

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == (end - start).days + 1

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={
            timezone.now() - timedelta(days=4): timedelta(hours=3),
            timezone.now() - timedelta(days=2): timedelta(hours=2),
            timezone.now() - timedelta(days=1): timedelta(hours=1),
        },
        loadings={
            timezone.now(): timedelta(hours=8),
            timezone.now() + timedelta(days=1): timedelta(hours=1),
        },
        issues_counts={timezone.now() + timedelta(days=1): 1},
        time_estimates={
            timezone.now() + timedelta(days=1): timedelta(hours=15),
        },
        time_remains={
            timezone.now()
            + timedelta(days=1): timedelta(
                seconds=issue.time_estimate - issue.total_time_spent,
            ),
        },
    )


def test_negative_remains(team, team_developer, team_leader):
    """
    Test negative remains.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    issue = IssueFactory.create(user=team_developer, due_date=datetime.now())

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=2)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.due_date = timezone.now() + timedelta(days=1)
    issue.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == 2

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == (end - start).days + 1

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={timezone.now() - timedelta(days=4): timedelta(hours=3)},
        issues_counts={timezone.now() + timedelta(days=1): 1},
        time_estimates={
            timezone.now() + timedelta(days=1): timedelta(hours=2),
        },
    )


def test_loading_day_already_has_spends(team, team_developer, team_leader):
    """
    Test loading day already has spends.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    issues = [
        IssueFactory.create(user=team_developer, due_date=datetime.now()),
        IssueFactory.create(
            user=team_developer,
            total_time_spent=timedelta(hours=3).total_seconds(),
            time_estimate=timedelta(hours=10).total_seconds(),
        ),
    ]

    IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=team_developer,
        base=issues[1],
        time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=team_developer,
        base=issues[1],
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=team_developer,
        base=issues[0],
        time_spent=seconds(hours=3),
    )

    issues[0].time_estimate = int(seconds(hours=4))
    issues[0].total_time_spent = int(seconds(hours=3))
    issues[0].due_date = timezone.now()
    issues[0].save()

    issues[1].total_time_spent = issues[1].time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issues[1].save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == 2

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == (end - start).days + 1

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={timezone.now(): timedelta(hours=6)},
        loadings={
            timezone.now(): timedelta(hours=8),
            timezone.now() + timedelta(days=1): timedelta(hours=6),
        },
        issues_counts={timezone.now(): 1},
        time_estimates={timezone.now(): timedelta(hours=4)},
        time_remains={
            timezone.now(): timedelta(
                seconds=issues[0].time_estimate - issues[0].total_time_spent,
            ),
        },
    )


def test_not_in_range(team, team_developer, team_leader):
    """
    Test not in range.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    issue = IssueFactory.create(
        user=team_developer,
        due_date=datetime.now(),
        time_estimate=0,
        total_time_spent=0,
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=5, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() + timedelta(days=1),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=3),
    )

    start = timezone.now().date() - timedelta(days=3)
    end = timezone.now().date() + timedelta(days=3)
    metrics = get_progress_metrics(team, start, end, GroupProgressMetrics.DAY)

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == (end - start).days + 1

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={
            timezone.now() - timedelta(days=1): timedelta(hours=1),
            timezone.now() + timedelta(days=1): timedelta(hours=3),
        },
        issues_counts={timezone.now(): 1},
    )


def test_another_user_not_in_team(team, team_developer, team_leader):
    """
    Test another user not in team.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    issue = IssueFactory.create(
        user=team_developer,
        due_date=datetime.now(),
        time_estimate=0,
        total_time_spent=0,
    )

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2, hours=5),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=3),
    )

    metrics = get_progress_metrics(
        team,
        timezone.now().date() - timedelta(days=5),
        timezone.now().date() + timedelta(days=5),
        GroupProgressMetrics.DAY,
    )

    assert len(metrics) == 2
    assert not any(metric.user == another_user for metric in metrics)


def test_another_user_in_team(  # noqa: WPS211
    team,
    team_developer,
    team_leader,
    make_team_developer,
    issue,
    another_user,
):
    """
    Test another user in team.

    :param team:
    :param team_developer:
    :param team_leader:
    :param make_team_developer:
    """
    make_team_developer(team, another_user)

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2, hours=3),
        user=team_developer,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1, hours=5),
        user=team_developer,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=timezone.now() + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=3),
    )

    issue.time_estimate = seconds(hours=4)
    issue.total_time_spent = 0
    issue.save()

    start = timezone.now().date() - timedelta(days=5)
    end = timezone.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(team, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == 3

    developer_metrics = next(
        metric.metrics for metric in metrics if metric.user == team_developer
    )

    assert len(developer_metrics) == (end - start).days + 1

    checkers.check_user_progress_metrics(
        developer_metrics,
        spents={
            timezone.now() - timedelta(days=2, hours=3): timedelta(hours=2),
            timezone.now() - timedelta(days=1, hours=3): -timedelta(hours=3),
        },
        loadings={timezone.now(): timedelta(hours=4)},
        issues_counts={timezone.now(): 1},
        time_estimates={timezone.now(): timedelta(hours=4)},
        time_remains={timezone.now(): timedelta(hours=4)},
    )

    another_user_metrics = next(
        metric.metrics for metric in metrics if metric.user == another_user
    )

    assert len(another_user_metrics) == (end - start).days + 1

    checkers.check_user_progress_metrics(
        another_user_metrics,
        spents={
            timezone.now() - timedelta(days=1, hours=3): timedelta(hours=4),
            timezone.now() + timedelta(days=1): timedelta(hours=3),
        },
    )
