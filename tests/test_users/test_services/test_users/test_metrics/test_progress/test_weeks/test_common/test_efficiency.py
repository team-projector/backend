from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from jnt_django_toolbox.helpers.date import begin_of_week, date2datetime
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.logic.services.user.progress.main import (
    GroupProgressMetrics,
    get_progress_metrics,
)
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_weeks import (  # noqa: E501
    checkers,
)


def test_efficiency_more100(user):
    """
    Test efficiency more100.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    issue = IssueFactory.create(
        user=user,
        due_date=monday + timedelta(days=1),
        time_estimate=seconds(hours=15),
        state=IssueState.CLOSED,
        closed_at=timezone.make_aware(
            date2datetime(monday + timedelta(days=1)),
        ),
    )

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.save()

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        GroupProgressMetrics.WEEK,
    )

    assert len(metrics) == 2
    checkers.check_user_progress_metrics(
        metrics,
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
        efficiencies={monday: issue.time_estimate / issue.total_time_spent},
    )


def test_efficiency_less100(user):
    """
    Test efficiency less100.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        state=IssueState.CLOSED,
        due_date=monday + timedelta(days=1),
        closed_at=timezone.make_aware(
            date2datetime(monday + timedelta(days=1)),
        ),
    )

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.save()

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        GroupProgressMetrics.WEEK,
    )

    assert len(metrics) == 2
    checkers.check_user_progress_metrics(
        metrics,
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=3)},
        efficiencies={monday: issue.time_estimate / issue.total_time_spent},
    )


def test_efficiency_zero_estimate(user):
    """
    Test efficiency zero estimate.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    issue = IssueFactory.create(
        user=user,
        state=IssueState.CLOSED,
        time_estimate=0,
        due_date=monday + timedelta(days=1),
        closed_at=timezone.make_aware(
            date2datetime(monday + timedelta(days=1)),
        ),
    )

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.save()

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        GroupProgressMetrics.WEEK,
    )

    assert len(metrics) == 2
    checkers.check_user_progress_metrics(
        metrics,
        spents={monday: timedelta(hours=6)},
        issues_counts={monday: 1},
    )


def test_efficiency_zero_spend(user):
    """
    Test efficiency zero spend.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=0,
        state=IssueState.CLOSED,
        due_date=monday + timedelta(days=1),
        closed_at=timezone.make_aware(
            date2datetime(monday + timedelta(days=1)),
        ),
    )

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        GroupProgressMetrics.WEEK,
    )

    assert len(metrics) == 2
    checkers.check_user_progress_metrics(
        metrics,
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=2)},
    )
