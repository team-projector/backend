from jnt_django_toolbox.helpers.time import seconds

from apps.development.graphql.types import MergeRequestType
from apps.development.models.issue import IssueState
from apps.development.services.merge_request.problems import (
    PROBLEM_EMPTY_ESTIMATE,
    PROBLEM_NOT_ASSIGNED,
    get_merge_request_problems,
)
from tests.test_development.factories import (
    IssueFactory,
    LabelFactory,
    MergeRequestFactory,
)


def test_empty_estimate(user):
    """
    Test empty estimate.

    :param user:
    """
    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        time_estimate=None,
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = get_merge_request_problems(merge_request)

    assert problems == [PROBLEM_EMPTY_ESTIMATE]


def test_empty_estimate_but_closed(user):
    """
    Test empty estimate but closed.

    :param user:
    """
    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.CLOSED,
        time_estimate=None,
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = get_merge_request_problems(merge_request)
    assert not problems


def test_zero_estimate(user):
    """
    Test zero estimate.

    :param user:
    """
    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        time_estimate=0,
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = get_merge_request_problems(merge_request)

    assert problems == [PROBLEM_EMPTY_ESTIMATE]


def test_not_assigned(user):
    """
    Test not assigned.

    :param user:
    """
    label_done = LabelFactory.create(title="Done")

    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        time_estimate=seconds(hours=1),
    )
    problem_issue.labels.add(label_done)

    merge_request = MergeRequestFactory.create(user=None)
    merge_request.issues.add(problem_issue)

    problems = get_merge_request_problems(merge_request)

    assert problems == [PROBLEM_NOT_ASSIGNED]


def test_not_assigned_but_closed(user):
    """
    Test not assigned but closed.

    :param user:
    """
    label_done = LabelFactory.create(title="Done")

    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.CLOSED,
        time_estimate=seconds(hours=1),
    )
    problem_issue.labels.add(label_done)

    merge_request = MergeRequestFactory.create(user=None)
    merge_request.issues.add(problem_issue)

    problems = get_merge_request_problems(merge_request)
    assert not problems


def test_two_errors_per_merge_request(user):
    """
    Test two errors per merge request.

    :param user:
    """
    label_done = LabelFactory.create(title="Done")

    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        time_estimate=0,
    )
    problem_issue.labels.add(label_done)

    merge_request = MergeRequestFactory.create(user=None)
    merge_request.issues.add(problem_issue)

    problems = get_merge_request_problems(merge_request)

    assert problems == [PROBLEM_EMPTY_ESTIMATE, PROBLEM_NOT_ASSIGNED]


def test_resolver(user):
    """
    Test resolver.

    :param user:
    """
    problem_issue = IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        time_estimate=None,
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = MergeRequestType.resolve_problems(merge_request, None)

    assert problems == [PROBLEM_EMPTY_ESTIMATE]
