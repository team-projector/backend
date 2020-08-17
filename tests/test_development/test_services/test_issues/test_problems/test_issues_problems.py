# -*- coding: utf-8 -*-

from apps.development.services.issue.problems import get_issue_problems
from apps.development.services.issue.problems.checkers import (
    PROBLEM_EMPTY_DUE_DAY,
    PROBLEM_EMPTY_ESTIMATE,
)
from tests.test_development.factories import IssueFactory


def test_two_errors_per_issue(user):
    """
    Test two errors per issue.

    :param user:
    """
    issue = IssueFactory.create(user=user, time_estimate=None, due_date=None)

    problems = get_issue_problems(issue)
    assert set(problems) == {PROBLEM_EMPTY_ESTIMATE, PROBLEM_EMPTY_DUE_DAY}
