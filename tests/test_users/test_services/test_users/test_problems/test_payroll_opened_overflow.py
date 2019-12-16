# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.users.services import user as user_service
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_detect(user):
    """Test if user has many opened tasks."""
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=5),
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=8),
    )

    assert user_service.get_problems(user) == [
        user_service.PROBLEM_NOT_ENOUGH_TASKS,
        user_service.PROBLEM_PAYROLL_OPENED_OVERFLOW,
    ]
