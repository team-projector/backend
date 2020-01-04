# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import ISSUE_STATES, Issue
from tests.test_development.factories import IssueFactory


def test_filter_by_due_date_and_state(user):
    issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.OPENED,
        due_date=datetime.now()
    )
    IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        due_date=datetime.now()
    )
    IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        due_date=datetime.now() - timedelta(days=1)
    )
    IssueFactory.create(
        user=user,
        state=ISSUE_STATES.OPENED,
        due_date=datetime.now() - timedelta(days=1)
    )

    results = IssuesFilterSet(
        data={
            "due_date": datetime.now().date(),
            "state": ISSUE_STATES.OPENED
        },
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue
