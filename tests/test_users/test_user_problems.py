import pytest

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.users.graphql.types.user import UserType
from apps.users.services import user as user_service
from apps.users.services.user.problems.checkers.base import BaseProblemChecker
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestFactory,
)
from tests.test_users.factories import UserFactory


@pytest.fixture
def user(db):
    yield UserFactory.create(daily_work_hours=8)


def test_base_checker_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseProblemChecker().has_problem(user=None)


def test_no_problems(user):
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=5),
        total_time_spent=seconds(hours=1),
        state=ISSUE_STATES.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=4),
        total_time_spent=0,
        state=ISSUE_STATES.OPENED,
    )

    assert user_service.get_problems(user) == []


def test_not_enough_tasks_issues(user):
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=1),
        state=ISSUE_STATES.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=1),
        state=ISSUE_STATES.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=8),
        total_time_spent=0,
        state=ISSUE_STATES.CLOSED,
    )

    assert user_service.get_problems(user) == [
        user_service.PROBLEM_NOT_ENOUGH_TASKS]


def test_not_enough_tasks_merge_requests(user):
    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=1),
        state=MERGE_REQUESTS_STATES.OPENED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=1),
        state=MERGE_REQUESTS_STATES.OPENED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=8),
        total_time_spent=0,
        state=MERGE_REQUESTS_STATES.CLOSED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=8),
        total_time_spent=0,
        state=MERGE_REQUESTS_STATES.MERGED,
    )

    assert user_service.get_problems(user) == [
        user_service.PROBLEM_NOT_ENOUGH_TASKS]


def test_not_enough_tasks_complex(user):
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=1),
        state=ISSUE_STATES.OPENED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=1),
        state=MERGE_REQUESTS_STATES.OPENED,
    )

    assert user_service.get_problems(user) == [
        user_service.PROBLEM_NOT_ENOUGH_TASKS]


def test_payroll_opened_overflow(user):
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
        user_service.PROBLEM_PAYROLL_OPENED_OVERFLOW]


def test_resolver(user):
    IssueSpentTimeFactory.create(
        user=user,
        time_spent=seconds(hours=16)
    )

    problems = UserType.resolve_problems(user, None)
    assert problems == [user_service.PROBLEM_NOT_ENOUGH_TASKS,
                        user_service.PROBLEM_PAYROLL_OPENED_OVERFLOW]
