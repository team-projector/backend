# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.users.graphql.types.user import UserType
from apps.users.services import user as user_service
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_resolver(user):
    """Test user problems resolver."""
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=16)
    )

    problems = UserType.resolve_problems(user, None)
    assert problems == [
        user_service.PROBLEM_NOT_ENOUGH_TASKS,
        user_service.PROBLEM_PAYROLL_OPENED_OVERFLOW,
    ]
