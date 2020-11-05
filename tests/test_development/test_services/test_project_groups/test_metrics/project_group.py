from datetime import timedelta

import pytest

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
)
from tests.test_payroll.factories import IssueSpentTimeFactory


@pytest.fixture()
def user(user):
    """Update user fixture."""
    user.tax_rate = 0.3
    user.hour_rate = 50
    user.customer_hour_rate = 80
    user.save()

    return user


@pytest.fixture()
def project_group(db):
    """Create project group."""
    project_group = ProjectGroupFactory.create()
    ProjectGroupMilestoneFactory.create(
        owner=project_group,
        budget=500,
    )
    return project_group


@pytest.fixture()
def projects(project_group):
    """Create projects."""
    return ProjectFactory.create_batch(3, group=project_group)


@pytest.fixture()
def issues(projects):
    """Create issues."""
    return [_add_issue(project) for project in projects]


def test_metrics(user, project_group, issues):
    """Test project metrics."""
    issue = issues[0]
    issue.user = user
    issue.save()

    _add_spent_time(issue, user, timedelta(hours=1).total_seconds())
    _generate_payroll(user, issue.created_at)

    metrics = get_project_group_metrics(project_group)

    assert metrics.budget == 500
    assert metrics.budget_remains == 420
    assert metrics.budget_spent == 80
    assert metrics.payroll == 50
    assert metrics.profit == 450


def test_some_milestones(user):
    """Test with some milestones."""
    milestone1 = ProjectGroupMilestoneFactory.create(
        budget=500,
    )
    milestone2 = ProjectGroupMilestoneFactory.create(
        budget=300,
        owner=milestone1.owner,
    )

    project = ProjectFactory.create(group=milestone1.owner)

    issue1 = _add_issue(project, milestone1)
    issue2 = _add_issue(project, milestone2)

    _add_spent_time(issue1, user, timedelta(hours=1).total_seconds())
    _add_spent_time(issue2, user, timedelta(hours=3).total_seconds())

    _generate_payroll(user, issue1.created_at)

    metrics = get_project_group_metrics(milestone1.owner)

    assert metrics.budget == 800
    assert metrics.budget_remains == 480
    assert metrics.budget_spent == 320
    assert metrics.payroll == 200
    assert metrics.profit == 600


def test_empty(user, project_group, issues):
    """Test empty project group."""
    issue = issues[0]
    issue.user = user
    issue.save()

    _add_spent_time(issue, user, timedelta(hours=1).total_seconds())
    _generate_payroll(user, issue.created_at)

    project_group.milestones.clear()

    metrics = get_project_group_metrics(project_group)

    assert not metrics.budget
    assert not metrics.budget_remains
    assert not metrics.budget_spent
    assert not metrics.payroll
    assert not metrics.profit


def _add_issue(project, milestone=None) -> Issue:
    """Create issue."""
    milestone = milestone or project.group.milestones.first()

    return IssueFactory.create(
        project=project,
        milestone=milestone,
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
