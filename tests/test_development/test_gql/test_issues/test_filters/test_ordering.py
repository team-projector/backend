from datetime import datetime, timedelta

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory

KEY_ORDERING = "order_by"


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
        data={KEY_ORDERING: "title"},
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
        data={KEY_ORDERING: "-title"},
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
        data={KEY_ORDERING: "dueDate"},
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
        data={KEY_ORDERING: "-dueDate"},
        queryset=Issue.objects.all(),
    ).qs

    assert list(queryset) == issues[::-1]
