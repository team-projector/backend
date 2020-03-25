# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import IssueFactory


def test_opened(user):
    """Test filter by opened state."""
    issue = IssueFactory.create(user=user, state=IssueState.OPENED)
    IssueFactory.create_batch(5, user=user, state="")

    results = IssuesFilterSet(
        data={"state": IssueState.OPENED}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == issue


def test_closed(user):
    """Test filter by closed state."""
    IssueFactory.create_batch(5, user=user, state="")
    issue = IssueFactory.create(user=user, state=IssueState.CLOSED)

    results = IssuesFilterSet(
        data={"state": IssueState.CLOSED}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == issue
