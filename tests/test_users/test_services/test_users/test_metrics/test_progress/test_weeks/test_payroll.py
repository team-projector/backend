# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.utils import timezone
from jnt_django_toolbox.helpers.date import begin_of_week
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.services.user.metrics import get_progress_metrics
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.test_services.test_users.test_metrics.test_progress.test_weeks import (  # noqa: E501
    checkers,
)


def test_opened(user):
    """
    Test opened.

    :param user:
    """
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, due_date=datetime.now())
    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday,
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
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        "week",
    )

    checkers.check_user_progress_payroll_metrics(
        metrics,
        payroll={monday: 6 * user.hour_rate},
        paid={monday: 0},
    )


def test_paid(user):
    """
    Test paid.

    :param user:
    """
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=IssueState.CLOSED,
    )
    monday = begin_of_week(timezone.now().date())

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=3),
    )

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        "week",
    )

    checkers.check_user_progress_payroll_metrics(
        metrics,
        payroll={monday: 0},
        paid={monday: 6 * user.hour_rate},
    )


def test_closed(user):
    """
    Test closed.

    :param user:
    """
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=IssueState.CLOSED,
    )
    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday,
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
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        "week",
    )

    checkers.check_user_progress_payroll_metrics(
        metrics,
        payroll={monday: 6 * user.hour_rate},
        paid={monday: 0},
    )


def test_complex(user):
    """
    Test complex.

    :param user:
    """
    user.hour_rate = 100
    user.save()

    monday = begin_of_week(timezone.now().date())

    salary = SalaryFactory.create(user=user)

    closed_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=IssueState.CLOSED,
    )
    opened_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        state=IssueState.OPENED,
    )

    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=closed_issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=opened_issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=opened_issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=opened_issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        salary=salary,
        base=closed_issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=opened_issue,
        time_spent=-seconds(hours=3),
    )

    metrics = get_progress_metrics(
        user,
        monday - timedelta(days=5),
        monday + timedelta(days=5),
        "week",
    )

    checkers.check_user_progress_payroll_metrics(
        metrics,
        payroll={monday: 12 * user.hour_rate},
        paid={monday: 3 * user.hour_rate},
    )
