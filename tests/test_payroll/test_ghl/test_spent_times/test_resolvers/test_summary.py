# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.payroll.graphql.resolvers import resolve_spent_times_summary
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_payroll.test_services.test_spent_times.test_summary import (
    checkers,
)


def test_resolver(user, ghl_auth_mock_info):
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user),
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=IssueState.CLOSED),
        time_spent=seconds(hours=1),
    )

    summary = resolve_spent_times_summary(
        parent=None, info=ghl_auth_mock_info, state=IssueState.OPENED,
    )

    checkers.check_time_spent_summary(
        summary, spent=seconds(hours=2), opened_spent=seconds(hours=2),
    )
    checkers.check_time_spent_issues_summary(
        summary.issues,
        opened_spent=seconds(hours=2),
        closed_spent=seconds(hours=0),
        spent=seconds(hours=2),
    )
    checkers.check_time_spent_merge_requests_summary(summary.merge_requests)
