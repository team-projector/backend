from datetime import datetime, timedelta

import pytest

from apps.development.graphql.fields.issues import (
    IssuesConnectionField,
    IssueSort,
)
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory

KEY_ORDERING = "sort"


@pytest.fixture()
def sort_handler():
    """Returns sort handler."""
    return IssuesConnectionField.sort_handler


def test_by_title_asc(user, sort_handler):
    """
    Test order by title asc.

    :param user:
    """
    issues = [
        IssueFactory.create(title="agent", user=user),
        IssueFactory.create(title="bar", user=user),
        IssueFactory.create(title="cloud", user=user),
    ]

    queryset = sort_handler.filter(
        Issue.objects.all(),
        [IssueSort.TITLE_ASC.value],
    )

    assert list(queryset) == issues


def test_by_title_desc(user, sort_handler):
    """
    Test order by title desc.

    :param user:
    """
    issues = [
        IssueFactory.create(title="agent", user=user),
        IssueFactory.create(title="bar", user=user),
        IssueFactory.create(title="cloud", user=user),
    ]

    queryset = sort_handler.filter(
        Issue.objects.all(),
        [IssueSort.TITLE_DESC.value],
    )
    assert list(queryset) == issues[::-1]


def test_by_due_date_asc(user, sort_handler):
    """
    Test order by due date asc.

    :param user:
    """
    issues = [
        IssueFactory.create(
            due_date=datetime.now() - timedelta(days=3),
            user=user,
        ),
        IssueFactory.create(due_date=datetime.now(), user=user),
        IssueFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            user=user,
        ),
    ]

    queryset = sort_handler.filter(
        Issue.objects.all(),
        [IssueSort.DUE_DATE_ASC.value],
    )

    assert list(queryset) == issues


def test_by_due_date_desc(user, sort_handler):
    """
    Test order by due date desc.

    :param user:
    """
    issues = [
        IssueFactory.create(
            due_date=datetime.now() - timedelta(days=3),
            user=user,
        ),
        IssueFactory.create(due_date=datetime.now(), user=user),
        IssueFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            user=user,
        ),
    ]

    queryset = sort_handler.filter(
        Issue.objects.all(),
        [IssueSort.DUE_DATE_DESC.value],
    )

    assert list(queryset) == issues[::-1]
