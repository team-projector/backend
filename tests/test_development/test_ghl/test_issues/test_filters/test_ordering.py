from datetime import datetime, timedelta

from apps.development.graphql.filters import (
    IssuesFilterSet,
    TicketIssuesFilterSet,
)
from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


def test_by_title_asc(user):
    """
    Test order by title asc.

    :param user:
    """
    issues = [
        IssueFactory.create(title="agent", user=user),
        IssueFactory.create(title="bar", user=user),
        IssueFactory.create(title="cloud", user=user),
    ]

    queryset = IssuesFilterSet(
        data={"order_by": "title"},
        queryset=Issue.objects.all(),
    ).qs

    assert list(queryset) == issues


def test_by_title_desc(user):
    """
    Test order by title desc.

    :param user:
    """
    issues = [
        IssueFactory.create(title="agent", user=user),
        IssueFactory.create(title="bar", user=user),
        IssueFactory.create(title="cloud", user=user),
    ]

    queryset = IssuesFilterSet(
        data={"order_by": "-title"},
        queryset=Issue.objects.all(),
    ).qs

    assert list(queryset) == issues[::-1]


def test_by_due_date_asc(user):
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

    queryset = IssuesFilterSet(
        data={"order_by": "dueDate"},
        queryset=Issue.objects.all(),
    ).qs

    assert list(queryset) == issues


def test_by_due_date_desc(user):
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

    queryset = IssuesFilterSet(
        data={"order_by": "-dueDate"},
        queryset=Issue.objects.all(),
    ).qs

    assert list(queryset) == issues[::-1]


def test_by_user_state(user):
    """
    Test order by user state.

    :param user:
    """
    issues = [
        IssueFactory.create(
            title="title 1",
            due_date=datetime.now() - timedelta(days=3),
            user=UserFactory.create(),
            state=IssueState.OPENED,
        ),
        IssueFactory.create(
            title="title 2",
            due_date=datetime.now(),
            user=user,
            state=IssueState.CLOSED,
        ),
        IssueFactory.create(
            title="title 3",
            due_date=datetime.now() + timedelta(days=1),
            user=user,
        ),
    ]

    queryset = TicketIssuesFilterSet(
        data={"order_by": "user,state"},
        queryset=Issue.objects.all(),
    ).qs
    sorted_issues = [issues[1], issues[2], issues[0]]

    assert list(queryset) == sorted_issues
