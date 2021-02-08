from datetime import datetime, timedelta

from constance.test.pytest import override_config
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.services.user.metrics import get_progress_metrics
from apps.users.services.user.metrics.progress.main import GroupProgressMetrics
from tests.test_development.factories import IssueFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_days import (  # noqa: E501
    checkers,
)


def test_replay(user):
    """
    Test replay.

    :param user:
    """
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=0,
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        loadings={start: timedelta(hours=7)},
    )


def test_has_spents(user):
    """
    Test has spents.

    :param user:
    """
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=seconds(hours=2),
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        loadings={start: timedelta(hours=5)},
    )


def test_replay_without_active_issues(user):
    """
    Test replay without active issues.

    :param user:
    """
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=3),
        total_time_spent=3,
        state=IssueState.CLOSED,
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=3)
    metrics = get_progress_metrics(user, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        loadings={start: timedelta(seconds=0)},
    )


@override_config(WEEKENDS_DAYS=[0, 1, 2, 3, 4, 5, 6])
def test_not_apply_loading_weekends(user):
    """
    Test not apply loading weekends.

    :param user:
    """
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=0,
        state=IssueState.OPENED,
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, GroupProgressMetrics.DAY)

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        loadings={start: timedelta(seconds=0)},
    )
