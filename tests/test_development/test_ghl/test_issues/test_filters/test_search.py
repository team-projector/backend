# -*- coding: utf-8 -*-

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_title_single(user):
    issue = IssueFactory.create(title="create", user=user, gl_url="foobar")
    IssueFactory.create(title="react", user=user)

    results = IssuesFilterSet(
        data={"q": "ate"}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == issue


def test_by_title_many(user):
    issues = [
        IssueFactory.create(title="create", user=user, gl_url="foobar"),
        IssueFactory.create(title="react", user=user),
    ]

    results = IssuesFilterSet(
        data={"q": "rea"}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 2
    assert set(results) == set(issues)


def test_empty_results(user):
    IssueFactory.create(title="issue", user=user)

    results = IssuesFilterSet(
        data={"q": "012345"}, queryset=Issue.objects.all(),
    ).qs

    assert not results.exists()


def test_by_gl_url(user):
    issue = IssueFactory.create(title="create", user=user, gl_url="foobar")

    results = IssuesFilterSet(
        data={"q": "foobar"}, queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == issue
