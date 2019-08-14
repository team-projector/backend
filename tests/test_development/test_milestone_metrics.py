from datetime import timedelta

from apps.development.services.metrics.milestones import get_milestone_metrics
from tests.test_development.factories import (
    IssueFactory, ProjectMilestoneFactory
)
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_payrolls(user):
    user.hour_rate = 1000
    user.customer_hour_rate = 100
    user.save()

    milestone = ProjectMilestoneFactory.create(budget=10000)

    issue_1 = IssueFactory.create(user=user, milestone=milestone)
    issue_2 = IssueFactory.create(user=user, milestone=milestone)
    issue_3 = IssueFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user, base=issue_1, time_spent=timedelta(hours=1).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue_1, time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue_2, time_spent=-timedelta(hours=1).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue_3, time_spent=timedelta(hours=3).total_seconds()
    )

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 2000
    assert metrics.profit == 8000
    assert metrics.budget_remains == 9800


def test_payrolls_no_spents(user):
    user.hour_rate = 1000
    user.customer_hour_rate = 100
    user.save()

    milestone = ProjectMilestoneFactory.create(budget=10000)

    IssueFactory.create(user=user, milestone=milestone)
    IssueFactory.create(user=user, milestone=milestone)
    IssueFactory.create(user=user)

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 0
    assert metrics.profit == milestone.budget
    assert metrics.budget_remains == milestone.budget


def test_payrolls_no_issues(user):
    user.hour_rate = 1000
    user.customer_hour_rate = 100
    user.save()

    milestone = ProjectMilestoneFactory.create(budget=10000)

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 0
    assert metrics.profit == milestone.budget
    assert metrics.budget_remains == milestone.budget


def test_payrolls_no_budget(user):
    user.hour_rate = 1000
    user.customer_hour_rate = 100
    user.save()

    milestone = ProjectMilestoneFactory.create(budget=0)

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 0
    assert metrics.profit == milestone.budget
    assert metrics.budget_remains == milestone.budget
