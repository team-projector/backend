# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from apps.development.models.issue import IssueState
from apps.development.services.issue.problems import get_issue_problems
from apps.development.services.issue.problems.checkers import (
    PROBLEM_OVER_DUE_DAY,
)
from tests.test_development.factories import IssueFactory


def test_overdue_due_day(user):
    """
    Test overdue due day.

    :param user:
    """
    problem_issue = IssueFactory.create(
        user=user, due_date=datetime.now().date() - timedelta(days=1),
    )

    assert get_issue_problems(problem_issue) == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(user):
    """
    Test overdue due day but closed.

    :param user:
    """
    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date() - timedelta(days=1),
        state=IssueState.CLOSED,
    )

    assert not get_issue_problems(issue)
