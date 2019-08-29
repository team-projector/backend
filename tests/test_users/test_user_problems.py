import pytest

from apps.core.utils.time import seconds
from apps.users.services.problems.checkers.payroll_opened_overflow import (
    PROBLEM_PAYROLL_OPENED_OVERFLOW
)
from apps.users.graphql.types.user import UserType
from apps.users.services.problems.user import get_user_problems
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


@pytest.fixture
def user(db):
    yield UserFactory.create(daily_work_hours=8)


def test_no_problems(user):
    assert get_user_problems(user) == []


def test_payroll_opened_overflow(user):
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
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=4)
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=8)
    )

    assert get_user_problems(user) == []


def test_resolver(user):
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=16)
    )

    problems = UserType.resolve_problems(user, None)
    assert problems == [PROBLEM_PAYROLL_OPENED_OVERFLOW]
