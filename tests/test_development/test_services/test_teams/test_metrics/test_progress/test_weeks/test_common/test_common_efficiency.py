from datetime import datetime, timedelta

from django.db.models import Sum
from django.utils.timezone import make_aware
from jnt_django_toolbox.helpers.date import begin_of_week, date2datetime
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

METRICS_GROUP_WEEK = "week"


def test_efficiency_more100(team, team_developer, team_leader):
    """
    Test efficiency more100.

    :param team:
    :param team_developer:
    :param team_leader:
    """
    issue = IssueFactory.create(user=team_developer, due_date=datetime.now())

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
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = IssueState.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = make_aware(date2datetime(monday + timedelta(days=1)))
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
        efficiencies={monday: issue.time_estimate / issue.total_time_spent},
    )


def test_efficiency_less100(team, team_developer):
    """
    Test efficiency less100.

    :param team:
    :param team_developer:
    """
    issue = IssueFactory.create(user=team_developer, due_date=datetime.now())
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

    issue.time_estimate = seconds(hours=3)
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = IssueState.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = make_aware(date2datetime(monday + timedelta(days=1)))
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
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=3)},
        efficiencies={monday: issue.time_estimate / issue.total_time_spent},
    )


def test_efficiency_zero_estimate(team, team_developer):
    """
    Test efficiency zero estimate.

    :param team:
    :param team_developer:
    """
    issue = IssueFactory.create(user=team_developer, due_date=datetime.now())
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

    issue.time_estimate = 0
    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.state = IssueState.CLOSED
    issue.due_date = monday + timedelta(days=1)
    issue.closed_at = make_aware(date2datetime(monday + timedelta(days=1)))
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
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 1},
    )


def test_efficiency_zero_spend(team, team_developer):
    """
    Test efficiency zero spend.

    :param team:
    :param team_developer:
    """
    monday = begin_of_week(datetime.now().date(), get_first_week_day())
    IssueFactory.create(
        user=team_developer,
        time_estimate=seconds(hours=2),
        total_time_spent=0,
        state=IssueState.CLOSED,
        due_date=monday + timedelta(days=1),
        closed_at=make_aware(date2datetime(monday + timedelta(days=1))),
    )

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
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=2)},
    )
