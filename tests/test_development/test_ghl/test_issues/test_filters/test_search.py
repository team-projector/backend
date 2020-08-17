# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_title_single(user):
    """
    Test by title single.

    :param user:
    """
    issue = IssueFactory.create(title="create", user=user, gl_url="foobar")
    IssueFactory.create(title="react", user=user)

    queryset = IssuesFilterSet(
        data={"q": "ate"}, queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == issue


def test_by_title_many(user):
    """
    Test by title many.

    :param user:
    """
    issues = [
        IssueFactory.create(title="create", user=user, gl_url="foobar"),
        IssueFactory.create(title="react", user=user),
    ]

    queryset = IssuesFilterSet(
        data={"q": "rea"}, queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == set(issues)


def test_empty_queryset(user):
    """
    Test empty queryset.

    :param user:
    """
    IssueFactory.create(title="issue", user=user)

    queryset = IssuesFilterSet(
        data={"q": "012345"}, queryset=Issue.objects.all(),
    ).qs

    assert not queryset.exists()


def test_by_gl_url(user):
    """
    Test by gl url.

    :param user:
    """
    issue = IssueFactory.create(title="create", user=user, gl_url="foobar")

    queryset = IssuesFilterSet(
        data={"q": "foobar"}, queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == issue
