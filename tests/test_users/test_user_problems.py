from datetime import timedelta

from apps.users.services.problems.checkers.payroll_opened_overflow import (
    PROBLEM_PAYROLL_OPENED_OVERFLOW
)
from apps.users.services.problems.user import get_user_problems
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_no_problems(user):
    user.daily_work_hours = 8
    user.save(update_fields=['daily_work_hours'])

    assert get_user_problems(user) == []


def test_payroll_opened_overflow(user):
    user.daily_work_hours = 8
    user.save(update_fields=['daily_work_hours'])

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=timedelta(hours=5).total_seconds()
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=timedelta(hours=8).total_seconds()
    )

    assert get_user_problems(user) == [PROBLEM_PAYROLL_OPENED_OVERFLOW]


def test_no_payroll_opened_overflow(user):
    user.daily_work_hours = 8
    user.save(update_fields=['daily_work_hours'])

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=timedelta(hours=4).total_seconds()
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=timedelta(hours=8).total_seconds()
    )

    assert get_user_problems(user) == []
