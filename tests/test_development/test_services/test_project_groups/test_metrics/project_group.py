from datetime import timedelta

import pytest

from apps.development.models import Milestone
from apps.development.models.issue import Issue, IssueState
from apps.development.services.project_group.metrics import (
    get_project_group_metrics,
)
from apps.payroll.models import SpentTime
from apps.payroll.services.salary.calculator import SalaryCalculator
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
    ProjectMilestoneFactory,
)
from tests.test_payroll.factories import IssueSpentTimeFactory


@pytest.fixture()
def project_group(db):
    """Create project group."""
    return ProjectGroupFactory.create()


@pytest.fixture()
def projects(project_group):
    """Create projects."""
    return ProjectFactory.create_batch(3, group=project_group)


@pytest.fixture()
def project_milestones(projects):
    """Create milestones."""
    return [
        ProjectMilestoneFactory.create(owner=project, budget=150)
        for project in projects
    ]


@pytest.fixture()
def issues(projects, project_milestones):
    """Create issues."""
    return [_add_issue(project) for project in projects]


def test_metrics(user, project_group, issues):
    """Test project metrics."""
    user.tax_rate = 0.3
    user.hour_rate = 50
    user.customer_hour_rate = 80
    user.save()

    issue = issues[0]
    issue.user = user
    issue.save()

    ProjectGroupMilestoneFactory.create(
        owner=project_group,
        budget=500,
        gl_id=_get_project_group_milestone_id(),
    )

    _add_spent_time(issue, user, timedelta(hours=1).total_seconds())
    _generate_payroll(user, issue.created_at)

    metrics = get_project_group_metrics(project_group)

    assert metrics.budget == 500
    assert metrics.budget_remains == 420
    assert metrics.budget_spent == 80
    assert metrics.payroll == 50
    assert metrics.profit == 450


def _add_issue(project) -> Issue:
    """Create issue."""
    return IssueFactory.create(
        project=project,
        milestone=project.milestones.first(),
        state=IssueState.CLOSED,
        time_estimate=100,
        total_time_spent=70,
    )


def _add_spent_time(base, user, time_spent) -> SpentTime:
    """Add spent time for issue."""
    return IssueSpentTimeFactory.create(
        user=user,
        base=base,
        time_spent=time_spent,
    )


def _generate_payroll(user, payroll_date) -> None:
    """Generate salary for user."""
    calculator = SalaryCalculator(
        user,
        (payroll_date - timedelta(days=1)).date(),
        (payroll_date + timedelta(days=1)).date(),
    )

    calculator.generate(user)


def _get_project_group_milestone_id() -> int:
    queryset = Milestone.objects.order_by("-id").values("id")
    return queryset.first()["id"] + 1
