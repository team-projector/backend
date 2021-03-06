from datetime import datetime, timedelta

from django.db.models import Sum
from django.utils import timezone
from jnt_django_toolbox.helpers.date import begin_of_week
from jnt_django_toolbox.helpers.time import seconds

from apps.users.logic.services.user.progress import GroupProgressMetrics
from apps.users.logic.services.user.progress.main import get_progress_metrics
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_weeks import (  # noqa: E501
    checkers,
)

FIELD_TIME_SPENT = "time_spent"
KEY_SPENT = "spent"


def test_simple(user):
    """
    Test simple.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())

    issue = IssueFactory.create(
        user=user,
        due_date=monday + timedelta(days=1),
        closed_at=timezone.now(),
        time_estimate=seconds(hours=15),
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
        spent=Sum(FIELD_TIME_SPENT),
    )[KEY_SPENT]
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
    )


def test_many_weeks(user):
    """
    Test many weeks.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    issue = IssueFactory.create(
        user=user,
        closed_at=timezone.now(),
        time_estimate=seconds(hours=15),
        due_date=monday + timedelta(days=2),
    )

    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=2, hours=5),
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
        spent=Sum(FIELD_TIME_SPENT),
    )[KEY_SPENT]
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
        spents={
            monday - timedelta(weeks=1): timedelta(hours=5),
            monday: timedelta(hours=1),
        },
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_not_in_range(user):
    """
    Test not in range.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    issue = IssueFactory.create(
        user=user,
        closed_at=timezone.now(),
        time_estimate=seconds(hours=15),
        due_date=monday + timedelta(days=1),
    )

    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday - timedelta(days=2, hours=5),
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
        spent=Sum(FIELD_TIME_SPENT),
    )[KEY_SPENT]
    issue.save()

    metrics = get_progress_metrics(
        user,
        monday,
        monday + timedelta(weeks=1, days=5),
        GroupProgressMetrics.WEEK,
    )

    assert len(metrics) == 2
    checkers.check_user_progress_metrics(
        metrics,
        spents={monday: timedelta(hours=1)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_another_user(user):
    """
    Test another user.

    :param user:
    """
    monday = begin_of_week(timezone.now().date())
    issue = IssueFactory.create(
        user=user,
        closed_at=timezone.now(),
        time_estimate=seconds(hours=15),
        due_date=monday + timedelta(days=1),
    )

    another_user = UserFactory.create()

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

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum(FIELD_TIME_SPENT),
    )[KEY_SPENT]
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
        spents={monday: timedelta(hours=5)},
        issues_counts={monday: 1},
        time_estimates={monday: timedelta(hours=15)},
    )


def test_many_issues(user):
    """
    Test many issues.

    :param user:
    """
    monday = begin_of_week(datetime.now().date())
    issue = IssueFactory.create(
        user=user,
        closed_at=timezone.now(),
        time_estimate=seconds(hours=15),
        due_date=monday + timedelta(days=1),
    )

    another_issue = IssueFactory.create(
        user=user,
        due_date=monday + timedelta(days=4),
        total_time_spent=timedelta(hours=3).total_seconds(),
        time_estimate=timedelta(hours=10).total_seconds(),
    )

    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=4),
        user=user,
        base=another_issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=another_issue,
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
        spent=Sum(FIELD_TIME_SPENT),
    )[KEY_SPENT]
    issue.save()

    another_issue.total_time_spent = another_issue.time_spents.aggregate(
        spent=Sum(FIELD_TIME_SPENT),
    )[KEY_SPENT]
    another_issue.save()

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
        issues_counts={monday: 2},
        time_estimates={monday: timedelta(days=1, hours=1)},
    )
