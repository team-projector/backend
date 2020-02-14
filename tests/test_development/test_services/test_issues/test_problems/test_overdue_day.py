# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from apps.development.models.issue import ISSUE_STATES
from apps.development.services.issue.problems import get_issue_problems
from apps.development.services.issue.problems.checkers import (
    PROBLEM_OVER_DUE_DAY,
)
from tests.test_development.factories import IssueFactory


def test_overdue_due_day(user):
    problem_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date() - timedelta(days=1),
    )

    assert get_issue_problems(problem_issue) == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(user):
    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now().date() - timedelta(days=1),
        state=ISSUE_STATES.CLOSED,
    )

    assert not get_issue_problems(issue)