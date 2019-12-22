# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.users.services.user.problems import get_user_problems
from apps.users.services.user.problems.checkers import PROBLEM_NOT_ENOUGH_TASKS
from tests.test_development.factories import IssueFactory, MergeRequestFactory


def test_issues(user):
    """Test if not enough issues."""
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

    assert get_user_problems(user) == [
        PROBLEM_NOT_ENOUGH_TASKS,
    ]


def test_merge_requests(user):
    """Test if not enough merge requests."""
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

    assert get_user_problems(user) == [PROBLEM_NOT_ENOUGH_TASKS]


def test_complex(user):
    """Test if not enough merge requests and issues."""
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

    assert get_user_problems(user) == [PROBLEM_NOT_ENOUGH_TASKS]
