from datetime import datetime, timedelta

from apps.development.graphql.types.issue import IssueType
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.issue.problems import get_issue_problems
from apps.development.services.issue.problems.checkers import (
    PROBLEM_EMPTY_DUE_DAY,
    PROBLEM_EMPTY_ESTIMATE,
    PROBLEM_OVER_DUE_DAY,
)
from tests.test_development.factories import IssueFactory


def test_empty_due_day(user):
    problem_issue = IssueFactory.create(user=user)

    assert get_issue_problems(problem_issue) == [PROBLEM_EMPTY_DUE_DAY]


def test_empty_due_day_but_closed(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.CLOSED)

    assert get_issue_problems(issue) == []


def test_overdue_due_day(user):
    problem_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date() - timedelta(days=1)
    )

    assert get_issue_problems(problem_issue) == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(user):
    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date() - timedelta(days=1),
        state=ISSUE_STATES.CLOSED
    )

    assert get_issue_problems(issue) == []


def test_empty_estimate(user):
    problem_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date(),
        time_estimate=None
    )

    assert get_issue_problems(problem_issue) == [PROBLEM_EMPTY_ESTIMATE]


def test_zero_estimate(user):
    problem_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date(),
        time_estimate=0
    )

    assert get_issue_problems(problem_issue) == [PROBLEM_EMPTY_ESTIMATE]


def test_two_errors_per_issue(user):
    problem_issue = IssueFactory.create(user=user, time_estimate=None)

    problems = get_issue_problems(problem_issue)
    assert set(problems) == {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY}


def test_resolver(user):
    problem_issue = IssueFactory.create(user=user)

    problems = IssueType.resolve_problems(problem_issue, None)
    assert problems == [PROBLEM_EMPTY_DUE_DAY]
