# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.users.graphql.types.user import UserType
from apps.users.services.user.problems.checkers import (
    PROBLEM_NOT_ENOUGH_TASKS,
    PROBLEM_PAYROLL_OPENED_OVERFLOW,
)
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_resolver(user):
    """Test user problems resolver."""
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=16)
    )

    problems = UserType.resolve_problems(user, None)
    assert problems == [
        PROBLEM_NOT_ENOUGH_TASKS,
        PROBLEM_PAYROLL_OPENED_OVERFLOW,
    ]
