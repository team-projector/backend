# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory


def test_by_title_asc(user):
    issues = [
        IssueFactory.create(title="agent", user=user),
        IssueFactory.create(title="bar", user=user),
        IssueFactory.create(title="cloud", user=user),
    ]

    results = IssuesFilterSet(
        data={"order_by": "title"},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == issues


def test_by_title_desc(user):
    issues = [
        IssueFactory.create(title="agent", user=user),
        IssueFactory.create(title="bar", user=user),
        IssueFactory.create(title="cloud", user=user),
    ]

    results = IssuesFilterSet(
        data={"order_by": "-title"},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == issues[::-1]


def test_by_due_date_asc(user):
    issues = [
        IssueFactory.create(
            due_date=datetime.now() - timedelta(days=3),
            user=user,
        ),
        IssueFactory.create(due_date=datetime.now(), user=user),
        IssueFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            user=user,
        )
    ]

    results = IssuesFilterSet(
        data={"order_by": "dueDate"},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == issues


def test_by_due_date_desc(user):
    issues = [
        IssueFactory.create(
            due_date=datetime.now() - timedelta(days=3),
            user=user,
        ),
        IssueFactory.create(due_date=datetime.now(), user=user),
        IssueFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            user=user,
        )
    ]

    results = IssuesFilterSet(
        data={"order_by": "-dueDate"},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == issues[::-1]
