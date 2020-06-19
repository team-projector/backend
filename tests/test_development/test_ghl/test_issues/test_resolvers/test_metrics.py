# -*- coding: utf-8 -*-

from jnt_django_toolbox.helpers.time import seconds

from apps.development.graphql.types.issue import IssueType
from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_issues.test_metrics import (
    checkers,
)
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_resolver(user, ghl_auth_mock_info):
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=6),
    )

    checkers.check_issues_metrics(
        IssueType.resolve_metrics(issue, ghl_auth_mock_info),
        paid=6 * user.hour_rate,
    )
