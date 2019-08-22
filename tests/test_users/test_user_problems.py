from apps.users.services.problems.checkers.payroll_opened_overflow import (
    PROBLEM_PAYROLL_OPENED_OVERFLOW
)
from apps.users.services.problems.user import get_user_problems
from apps.core.utils.time import seconds
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
        time_spent=seconds(hours=5)
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=8)
    )

    assert get_user_problems(user) == [PROBLEM_PAYROLL_OPENED_OVERFLOW]


def test_no_payroll_opened_overflow(user):
    user.daily_work_hours = 8
    user.save(update_fields=['daily_work_hours'])

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=4)
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=8)
    )

    assert get_user_problems(user) == []
