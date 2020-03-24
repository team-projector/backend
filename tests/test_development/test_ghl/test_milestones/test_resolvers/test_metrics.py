# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.development.graphql.types.milestone import MilestoneType
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.test_services.test_milestones.helpers import (
    checkers,
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


def test_resolver(db):
    user = UserFactory.create(customer_hour_rate=100, hour_rate=1000)
    milestone = ProjectMilestoneFactory.create(budget=10000)

    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, milestone=milestone),
        time_spent=seconds(hours=1),
    )

    checkers.check_milestone_metrics(
        MilestoneType.resolve_metrics(milestone, None),
        budget=10000,
        payroll=1000,
        profit=9000,
        budget_remains=9900,
        budget_spent=100,
        issues_count=1,
        issues_opened_count=1,
    )
