# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import ISSUE_STATES, Issue
from tests.test_development.factories import IssueFactory


def test_opened(user):
    """Test filter by opened state."""
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)
    IssueFactory.create_batch(5, user=user, state="")

    results = IssuesFilterSet(
        data={"state": ISSUE_STATES.OPENED},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue


def test_closed(user):
    """Test filter by closed state."""
    IssueFactory.create_batch(5, user=user, state="")
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.CLOSED)

    results = IssuesFilterSet(
        data={"state": ISSUE_STATES.CLOSED},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue
