# -*- coding: utf-8 -*-

from datetime import datetime

from apps.development.services.issue.problems import get_issue_problems
from apps.development.services.issue.problems.checkers import (
    PROBLEM_EMPTY_ESTIMATE,
)
from tests.test_development.factories import IssueFactory


def test_empty_estimate(user):
    """
    Test empty estimate.

    :param user:
    """
    issue = IssueFactory.create(
        user=user, due_date=datetime.now().date(), time_estimate=None,
    )

    assert get_issue_problems(issue) == [PROBLEM_EMPTY_ESTIMATE]


def test_zero_estimate(user):
    """
    Test zero estimate.

    :param user:
    """
    issue = IssueFactory.create(
        user=user, due_date=datetime.now().date(), time_estimate=0,
    )

    assert get_issue_problems(issue) == [PROBLEM_EMPTY_ESTIMATE]
