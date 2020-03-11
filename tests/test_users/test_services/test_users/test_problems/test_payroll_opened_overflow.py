# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.users.services.user.problems import get_user_problems
from apps.users.services.user.problems.checkers import (
    PROBLEM_NOT_ENOUGH_TASKS,
    PROBLEM_PAYROLL_OPENED_OVERFLOW,
)
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_detect(user):
    """Test if user has many opened tasks."""
    IssueSpentTimeFactory.create(
        user=user, time_spent=seconds(hours=5),
    )

    IssueSpentTimeFactory.create(
        user=user, time_spent=seconds(hours=8),
    )

    assert get_user_problems(user) == [
        PROBLEM_NOT_ENOUGH_TASKS,
        PROBLEM_PAYROLL_OPENED_OVERFLOW,
    ]
