# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import pytest
from django.db.models import Sum
from django.utils import timezone

from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.users.services.user.metrics import get_progress_metrics
from apps.users.services.user.metrics.progress.provider import (
    ProgressMetricsProvider,
)
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_days import (  # noqa: E501
    checkers,
)


def test_simple(user, freeze_to_noon):
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=15),
        due_date=datetime.now() + timedelta(days=1),
    )

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.save()

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        spents={
            datetime.now() - timedelta(days=4): timedelta(hours=3),
            datetime.now() - timedelta(days=2): timedelta(hours=2),
            datetime.now() - timedelta(days=1): timedelta(hours=1),
        },
        loadings={
            datetime.now(): timedelta(hours=8),
            datetime.now() + timedelta(days=1): timedelta(hours=1),
        },
        issues_counts={datetime.now() + timedelta(days=1): 1},
        time_estimates={
            datetime.now() + timedelta(days=1): timedelta(hours=15),
        },
        time_remains={
            datetime.now()
            + timedelta(days=1): timedelta(
                seconds=issue.time_estimate - issue.total_time_spent,
            ),
        },
    )


def test_negative_remains(user, freeze_to_noon):
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        due_date=datetime.now() + timedelta(days=1),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )

    issue.total_time_spent = issue.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue.save()

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        spents={timezone.now() - timedelta(days=4): timedelta(hours=3)},
        issues_counts={timezone.now() + timedelta(days=1): 1},
        time_estimates={
            timezone.now() + timedelta(days=1): timedelta(hours=2),
        },
    )


def test_loading_day_already_has_spends(user, freeze_to_noon):
    issue = IssueFactory.create(
        user=user,
        time_estimate=int(seconds(hours=4)),
        total_time_spent=int(seconds(hours=3)),
        due_date=datetime.now(),
    )
    issue2 = IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        total_time_spent=seconds(hours=3),
        time_estimate=seconds(hours=10),
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue2,
        time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue2,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )

    issue2.total_time_spent = issue2.time_spents.aggregate(
        spent=Sum("time_spent"),
    )["spent"]
    issue2.save()

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        spents={timezone.now(): timedelta(hours=6)},
        loadings={
            timezone.now(): timedelta(hours=8),
            timezone.now() + timedelta(days=1): timedelta(hours=6),
        },
        issues_counts={timezone.now(): 1},
        time_estimates={timezone.now(): timedelta(hours=4)},
        time_remains={
            timezone.now(): timedelta(
                seconds=issue.time_estimate - issue.total_time_spent,
            ),
        },
    )


def test_not_in_range(user, freeze_to_noon):
    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        time_estimate=0,
        total_time_spent=0,
    )

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=5, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )

    start = datetime.now().date() - timedelta(days=3)
    end = datetime.now().date() + timedelta(days=3)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        spents={
            timezone.now() - timedelta(days=1): timedelta(hours=1),
            timezone.now() + timedelta(days=1): timedelta(hours=3),
        },
        issues_counts={timezone.now(): 1},
    )


def test_another_user(user, freeze_to_noon):
    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        time_estimate=0,
        total_time_spent=0,
    )

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=3),
    )

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        spents={
            timezone.now() - timedelta(days=2): timedelta(hours=2),
            timezone.now() - timedelta(days=1): -timedelta(hours=3),
        },
        issues_counts={timezone.now(): 1},
    )


def test_not_loading_over_daily_work_hours(user, freeze_to_noon):
    user.daily_work_hours = 4
    user.save()

    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=7),
        time_estimate=seconds(hours=15),
        total_time_spent=5,
        state=IssueState.OPENED,
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue,
        time_spent=seconds(hours=5),
    )

    start = datetime.now().date() - timedelta(days=1)
    end = datetime.now().date() + timedelta(days=1)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    checkers.check_user_progress_metrics(
        metrics,
        spents={
            timezone.now() - timedelta(days=1): timedelta(hours=0),
            timezone.now(): timedelta(hours=5),
        },
        loadings={
            timezone.now(): timedelta(hours=5),
            timezone.now() + timedelta(days=1): timedelta(hours=4),
        },
        issues_counts={timezone.now() + timedelta(days=7): 1},
        time_estimates={
            timezone.now() + timedelta(days=7): timedelta(hours=15),
        },
        planned_work_hours=4,
    )


def test_bad_group(user, freeze_to_noon):
    group = "test_bad_group"
    with pytest.raises(ValueError, match="Bad group '{0}'".format(group)):
        get_progress_metrics(
            user,
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
            group,
        )


def test_provider_not_implemented(user, freeze_to_noon):
    with pytest.raises(NotImplementedError):
        ProgressMetricsProvider(
            user,
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
        ).get_metrics()
