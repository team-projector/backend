# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import IssueFactory


def test_filter_by_due_date_and_state(user):
    issue = IssueFactory.create(
        user=user, state=IssueState.OPENED, due_date=datetime.now(),
    )
    IssueFactory.create(
        user=user, state=IssueState.CLOSED, due_date=datetime.now(),
    )
    IssueFactory.create(
        user=user,
        state=IssueState.CLOSED,
        due_date=datetime.now() - timedelta(days=1),
    )
    IssueFactory.create(
        user=user,
        state=IssueState.OPENED,
        due_date=datetime.now() - timedelta(days=1),
    )

    results = IssuesFilterSet(
        data={"due_date": datetime.now().date(), "state": IssueState.OPENED},
        queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == issue
