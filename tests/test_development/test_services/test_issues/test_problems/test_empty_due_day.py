# -*- coding: utf-8 -*-

from apps.development.models.issue import ISSUE_STATES
from apps.development.services.issue.problems import get_issue_problems
from apps.development.services.issue.problems.checkers import (
    PROBLEM_EMPTY_DUE_DAY,
)
from tests.test_development.factories import IssueFactory


def test_empty_due_day(user):
    issue = IssueFactory.create(user=user, due_date=None)

    assert get_issue_problems(issue) == [PROBLEM_EMPTY_DUE_DAY]


def test_empty_due_day_but_closed(user):
    issue = IssueFactory.create(
        user=user,
        due_date=None,
        state=ISSUE_STATES.CLOSED,
    )

    assert not get_issue_problems(issue)
