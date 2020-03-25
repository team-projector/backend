# -*- coding: utf-8 -*-

import pytest

from apps.core.utils.time import seconds
from apps.development.services.issue.metrics import get_user_time_spent
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def issue(db):
    """Create any issue."""
    return IssueFactory.create()


def test_without_user_spend(issue, user):
    """Test any user time spent for issue."""
    IssueSpentTimeFactory.create(
        user=UserFactory.create(),
        base=issue,
        time_spent=int(seconds(hours=2)),
    )

    assert get_user_time_spent(issue, user) == 0


def test_some_spends(issue, user):
    """Test user time spent for issue."""
    spends = [
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=2)),
        ),
    ]

    assert get_user_time_spent(issue, user) == sum(
        spent.time_spent for spent in spends
    )


def test_different_user_spents(issue, user):
    """Test user time spent with different spents for issue."""
    user_2 = UserFactory.create()
    spends = [
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            user=user_2, base=issue, time_spent=int(seconds(hours=2)),
        ),
    ]

    assert get_user_time_spent(issue, user) == spends[0].time_spent
    assert get_user_time_spent(issue, user_2) == spends[1].time_spent
