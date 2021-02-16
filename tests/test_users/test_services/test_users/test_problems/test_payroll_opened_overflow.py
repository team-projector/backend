from jnt_django_toolbox.helpers.time import seconds

from apps.users.logic.services.user.problems import (
    PROBLEM_NOT_ENOUGH_TASKS,
    PROBLEM_PAYROLL_OPENED_OVERFLOW,
)
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_detect(user, user_problems_service):
    """Test if user has many opened tasks."""
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=5),
    )

    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=8),
    )

    assert user_problems_service.get_problems(user) == [
        PROBLEM_NOT_ENOUGH_TASKS,
        PROBLEM_PAYROLL_OPENED_OVERFLOW,
    ]
