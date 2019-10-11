from apps.core.utils.time import seconds
from apps.development.graphql.types import MergeRequestType
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.merge_request import (
    get_problems, PROBLEM_EMPTY_ESTIMATE, PROBLEM_NOT_ASSIGNED
)
from tests.test_development.factories import (
    IssueFactory, LabelFactory, MergeRequestFactory
)


def test_empty_estimate(user):
    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.opened,
        time_estimate=None
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = get_problems(merge_request)

    assert problems == [PROBLEM_EMPTY_ESTIMATE]


def test_empty_estimate_but_closed(user):
    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.closed,
        time_estimate=None
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = get_problems(merge_request)

    assert problems == []


def test_zero_estimate(user):
    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.opened,
        time_estimate=0
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = get_problems(merge_request)

    assert problems == [PROBLEM_EMPTY_ESTIMATE]


def test_not_assigned(user):
    label_done = LabelFactory.create(title='Done')

    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.opened,
        time_estimate=seconds(hours=1),
    )
    problem_issue.labels.add(label_done)

    merge_request = MergeRequestFactory.create(user=None)
    merge_request.issues.add(problem_issue)

    problems = get_problems(merge_request)

    assert problems == [PROBLEM_NOT_ASSIGNED]


def test_not_assigned_but_closed(user):
    label_done = LabelFactory.create(title='Done')

    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.closed,
        time_estimate=seconds(hours=1),
    )
    problem_issue.labels.add(label_done)

    merge_request = MergeRequestFactory.create(user=None)
    merge_request.issues.add(problem_issue)

    problems = get_problems(merge_request)

    assert problems == []


def test_two_errors_per_merge_request(user):
    label_done = LabelFactory.create(title='Done')

    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.opened,
        time_estimate=0
    )
    problem_issue.labels.add(label_done)

    merge_request = MergeRequestFactory.create(user=None)
    merge_request.issues.add(problem_issue)

    problems = get_problems(merge_request)

    assert problems == [PROBLEM_EMPTY_ESTIMATE, PROBLEM_NOT_ASSIGNED]


def test_resolver(user):
    problem_issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.opened,
        time_estimate=None
    )

    merge_request = MergeRequestFactory.create(user=user)
    merge_request.issues.add(problem_issue)

    problems = MergeRequestType.resolve_problems(merge_request, None)

    assert problems == [PROBLEM_EMPTY_ESTIMATE]
