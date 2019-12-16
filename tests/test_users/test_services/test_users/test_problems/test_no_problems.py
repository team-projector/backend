# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.users.services import user as user_service
from tests.test_development.factories import IssueFactory


def test_no_problems(user):
    """Test if user has't any problem."""
    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=5),
        total_time_spent=seconds(hours=1),
        state=ISSUE_STATES.OPENED,
    )

    IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=4),
        total_time_spent=0,
        state=ISSUE_STATES.OPENED,
    )

    assert user_service.get_problems(user) == []
