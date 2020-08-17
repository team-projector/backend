# -*- coding: utf-8 -*-

from datetime import datetime

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_no_filter(user):
    """
    Test no filter.

    :param user:
    """
    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5, user=user, due_date=datetime.now().date(), time_estimate=1000,
    )

    issues = IssuesFilterSet(queryset=Issue.objects.all()).qs

    assert issues.count() == 7


def test_has_problems(user):
    """
    Test has problems.

    :param user:
    """
    issues = IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5, user=user, due_date=datetime.now().date(), time_estimate=1000,
    )

    queryset = IssuesFilterSet(
        data={"problems": True}, queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == set(issues)


def test_no_problems(user):
    """
    Test no problems.

    :param user:
    """
    issues = IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5, user=user, due_date=datetime.now().date(), time_estimate=1000,
    )

    queryset = IssuesFilterSet(
        data={"problems": False}, queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 5
    assert not any(issue in issues for issue in queryset)
