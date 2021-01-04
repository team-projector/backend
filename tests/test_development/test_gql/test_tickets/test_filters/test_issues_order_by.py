from datetime import datetime, timedelta

import pytest

from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue, IssueState
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def issues(user):
    """Create issues."""
    return (
        IssueFactory.create(
            title="title 0",
            due_date=datetime.now() - timedelta(days=3),
            user=UserFactory.create(),
            state=IssueState.OPENED,
        ),
        IssueFactory.create(
            title="title 1",
            due_date=datetime.now(),
            user=user,
            state=IssueState.CLOSED,
        ),
        IssueFactory.create(
            title="title 2",
            due_date=datetime.now() + timedelta(days=1),
            user=user,
            state=IssueState.OPENED,
        ),
        IssueFactory.create(
            title="title 3",
            due_date=datetime.now() + timedelta(days=1),
            user=None,
            state=IssueState.CLOSED,
        ),
        IssueFactory.create(
            title="title 4",
            due_date=datetime.now() + timedelta(days=1),
            user=user,
            state="",
        ),
    )


@pytest.mark.parametrize(
    ("order_by", "indexes"),
    [
        ("user,state", [4, 1, 2, 0, 3]),
        ("-user,state", [3, 0, 4, 1, 2]),
        ("user,-state", [2, 1, 4, 0, 3]),
        ("-user,-state", [3, 0, 2, 1, 4]),
    ],
)
def test_by_user_state(issues, order_by, indexes):
    """Test order by user state."""
    queryset = IssuesFilterSet(
        data={"order_by": order_by},
        queryset=Issue.objects.all(),
    ).qs

    assert list(queryset) == [issues[expected] for expected in indexes]
