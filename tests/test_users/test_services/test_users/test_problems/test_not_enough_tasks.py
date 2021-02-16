from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.users.logic.services.user.problems import PROBLEM_NOT_ENOUGH_TASKS
from tests.test_development.factories import IssueFactory, MergeRequestFactory


def test_issues(user, user_problems_service):
    """Test if not enough issues."""
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=1),
        state=IssueState.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=1),
        state=IssueState.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=8),
        total_time_spent=0,
        state=IssueState.CLOSED,
    )

    assert user_problems_service.get_problems(user) == [
        PROBLEM_NOT_ENOUGH_TASKS,
    ]


def test_merge_requests(user, user_problems_service):
    """Test if not enough merge requests."""
    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=1),
        state=MergeRequestState.OPENED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=1),
        state=MergeRequestState.OPENED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=8),
        total_time_spent=0,
        state=MergeRequestState.CLOSED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=8),
        total_time_spent=0,
        state=MergeRequestState.MERGED,
    )

    assert user_problems_service.get_problems(user) == [
        PROBLEM_NOT_ENOUGH_TASKS,
    ]


def test_complex(user, user_problems_service):
    """Test if not enough merge requests and issues."""
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=1),
        state=IssueState.OPENED,
    )

    MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=1),
        state=MergeRequestState.OPENED,
    )

    assert user_problems_service.get_problems(user) == [
        PROBLEM_NOT_ENOUGH_TASKS,
    ]
