# -*- coding: utf-8 -*-

from datetime import datetime

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_no_filter(user):
    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5, user=user, due_date=datetime.now().date(), time_estimate=1000,
    )

    results = IssuesFilterSet(queryset=Issue.objects.all()).qs

    assert results.count() == 7


def test_has_problems(user):
    issues = IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5, user=user, due_date=datetime.now().date(), time_estimate=1000,
    )

    results = IssuesFilterSet(
        data={"problems": True}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 2
    assert set(results) == set(issues)


def test_no_problems(user):
    issues = IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5, user=user, due_date=datetime.now().date(), time_estimate=1000,
    )

    results = IssuesFilterSet(
        data={"problems": False}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 5
    assert not any(issue in issues for issue in results)
