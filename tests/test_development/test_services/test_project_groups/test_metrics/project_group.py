from datetime import timedelta

import pytest

from apps.development.services.project_group.metrics import (
    get_project_group_metrics,
)
from tests.helpers.metrics import add_issue, add_spent_time, generate_payroll
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
)


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
    milestone = projects[0].group.milestones.first()
    issues = []
    for project_number, project in enumerate(projects):
        issues.append(add_issue(project, milestone, const=project_number + 1))
        issues.append(add_issue(project, milestone, const=project_number + 2))

    return issues


def test_metrics(user, project_group, issues):
    """Test project metrics."""
    issue = issues[0]
    issue.user = user
    issue.save()

    add_spent_time(issue, user, timedelta(hours=2).total_seconds())
    generate_payroll(user, issue.created_at)

    metrics = get_project_group_metrics(project_group)

    assert metrics.budget == 500
    assert metrics.budget_remains == 340
    assert metrics.budget_spent == 160
    assert metrics.payroll == 100
    assert metrics.profit == 400


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

    issue1 = add_issue(project, milestone1)

    add_spent_time(issue1, user, timedelta(hours=1).total_seconds())
    add_spent_time(
        add_issue(project, milestone2),
        user,
        timedelta(hours=3).total_seconds(),
    )

    generate_payroll(user, issue1.created_at)

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

    add_spent_time(issue, user, timedelta(hours=1).total_seconds())
    generate_payroll(user, issue.created_at)

    project_group.milestones.clear()

    metrics = get_project_group_metrics(project_group)

    assert not metrics.budget
    assert not metrics.budget_remains
    assert not metrics.budget_spent
    assert not metrics.payroll
    assert not metrics.profit
