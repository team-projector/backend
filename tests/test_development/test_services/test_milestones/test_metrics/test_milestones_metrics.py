import pytest

from apps.core.utils.time import seconds
from apps.development.graphql.types.milestone import MilestoneType
from apps.development.services.issue.metrics import (
    IssuesContainerMetricsProvider,
)
from apps.development.services.milestone.metrics import get_milestone_metrics
from tests.test_development.factories import (
    IssueFactory,
    MergeRequestFactory,
    ProjectMilestoneFactory,
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)
from tests.test_users.factories import UserFactory


@pytest.fixture()
def user(db):
    yield UserFactory.create(
        customer_hour_rate=100,
        hour_rate=1000,
    )


def test_filter_issues_not_implemented():
    with pytest.raises(NotImplementedError):
        IssuesContainerMetricsProvider().filter_issues(queryset=None)


def test_metrics_without_issues(user):
    milestone = ProjectMilestoneFactory.create(budget=10000)

    IssueFactory.create_batch(3, user=user)
    issue = IssueFactory.create(user=user)
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=1)
    )

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == 10000
    assert metrics.issues_count == 0
    assert metrics.payroll == 0
    assert metrics.budget_spent == 0
    assert metrics.time_spent == 0


def test_metrics_issues(user):
    milestone = ProjectMilestoneFactory.create(budget=10000)

    IssueFactory.create_batch(
        3,
        user=user,
        milestone=milestone,
        total_time_spent=0,
    )

    metrics = get_milestone_metrics(milestone)

    assert metrics.issues_count == 3
    assert metrics.issues_opened_count == 3
    assert metrics.issues_closed_count == 0
    assert metrics.payroll == 0
    assert metrics.budget_spent == 0
    assert metrics.time_spent == 0


def test_payrolls(user):
    milestone = ProjectMilestoneFactory.create(budget=10000)

    issue_1 = IssueFactory.create(user=user, milestone=milestone)
    issue_2 = IssueFactory.create(user=user, milestone=milestone)
    issue_3 = IssueFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user, base=issue_1, time_spent=seconds(hours=1)
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue_1, time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue_2, time_spent=-seconds(hours=1)
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue_3, time_spent=seconds(hours=3)
    )

    merge_request_1 = MergeRequestFactory.create(
        user=user, milestone=milestone
    )
    merge_request_2 = MergeRequestFactory.create(
        user=user, milestone=ProjectMilestoneFactory()
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request_1, time_spent=seconds(hours=1)
    )
    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request_2, time_spent=seconds(hours=10)
    )

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 3000
    assert metrics.profit == 7000
    assert metrics.budget_remains == 9700
    assert metrics.budget_spent == 300


def test_payrolls_no_spents(user):
    milestone = ProjectMilestoneFactory.create(budget=10000)

    IssueFactory.create(user=user, milestone=milestone)
    IssueFactory.create(user=user, milestone=milestone)
    IssueFactory.create(user=user)

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 0
    assert metrics.profit == milestone.budget
    assert metrics.budget_remains == milestone.budget
    assert metrics.budget_spent == 0


def test_payrolls_no_issues(db):
    milestone = ProjectMilestoneFactory.create(budget=10000)

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 0
    assert metrics.profit == milestone.budget
    assert metrics.budget_remains == milestone.budget
    assert metrics.budget_spent == 0


def test_payrolls_no_budget(db):
    milestone = ProjectMilestoneFactory.create(budget=0)

    metrics = get_milestone_metrics(milestone)

    assert metrics.budget == milestone.budget
    assert metrics.payroll == 0
    assert metrics.profit == milestone.budget
    assert metrics.budget_remains == milestone.budget
    assert metrics.budget_spent == 0


def test_resolver(user):
    milestone = ProjectMilestoneFactory.create(budget=10000)
    issue = IssueFactory.create(user=user, milestone=milestone)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=1)
    )

    metrics = MilestoneType.resolve_metrics(milestone, None)

    assert metrics.budget == 10000
    assert metrics.payroll == 1000
    assert metrics.profit == 9000
    assert metrics.budget_spent == 100
    assert metrics.budget_remains == 9900
