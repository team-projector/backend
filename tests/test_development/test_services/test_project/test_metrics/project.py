from datetime import timedelta

import pytest

from apps.development.services.project.metrics import get_project_metrics
from tests.helpers.metrics import add_issue, add_spent_time, generate_payroll
from tests.test_development.factories import ProjectMilestoneFactory


@pytest.fixture()
def user(user):
    """Update user."""
    user.tax_rate = 0.3
    user.hour_rate = 50
    user.customer_hour_rate = 80
    user.save()

    return user


@pytest.fixture()
def milestones(project):
    """Create milestones."""
    return ProjectMilestoneFactory.create_batch(2, owner=project, budget=150)


@pytest.fixture()
def issues(project, milestones):
    """Create issues."""
    issues = []

    for milestone_number, milestone in enumerate(milestones):
        issues.append(add_issue(project, milestone, milestone_number + 1))
        issues.append(add_issue(project, milestone, milestone_number + 2))

    return issues


def test_project_metrics(user, project, issues):
    """Test project metrics."""
    issue = issues[0]
    issue.user = user
    issue.save()

    add_spent_time(issue, user, timedelta(hours=1).total_seconds())
    generate_payroll(user, issue.created_at)

    metrics = get_project_metrics(project)

    assert metrics.budget == 300
    assert metrics.budget_remains == 220
    assert metrics.budget_spent == 80
    assert metrics.payroll == 50
    assert metrics.profit == 250


def test_project_metrics_negative_profit(user, project, issues):
    """Test project metrics negative profit."""
    issue = issues[0]
    issue.user = user
    issue.save()

    add_spent_time(issue, user, timedelta(hours=100).total_seconds())
    generate_payroll(user, issue.created_at)

    metrics = get_project_metrics(project)

    assert metrics.budget == 300
    assert metrics.budget_remains == -7700
    assert metrics.budget_spent == 8000
    assert metrics.payroll == 5000
    assert metrics.profit == -4700


def test_project_metrics_budget_empty(user, project, issues):
    """Test project metrics negative profit."""
    project.milestones.update(budget=0)

    issue = issues[0]
    issue.user = user
    issue.save()

    add_spent_time(issue, user, timedelta(hours=100).total_seconds())
    generate_payroll(user, issue.created_at)

    metrics = get_project_metrics(project)

    assert metrics.budget == 0
    assert metrics.budget_remains == -8000
    assert metrics.budget_spent == 8000
    assert metrics.payroll == 5000
    assert metrics.profit == -5000
