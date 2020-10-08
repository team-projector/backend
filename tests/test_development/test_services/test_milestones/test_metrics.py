import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.services.milestone.metrics import get_milestone_metrics
from tests.test_development.factories import (
    IssueFactory,
    MergeRequestFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.test_services.test_milestones.helpers import (
    checkers,
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)
from tests.test_users.factories import UserFactory


@pytest.fixture()
def user(db):
    """Test user."""
    return UserFactory.create(customer_hour_rate=100, hour_rate=1000)


@pytest.fixture()
def milestone(db):
    """Test milestone."""
    return ProjectMilestoneFactory.create(budget=10000)


def test_without_issues(user, milestone):
    """
    Test without issues.

    :param user:
    :param milestone:
    """
    IssueFactory.create_batch(3, user=user)
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user),
        time_spent=seconds(hours=1),
    )

    checkers.check_milestone_metrics(
        get_milestone_metrics(milestone),
        budget=10000,
        profit=10000,
        budget_remains=10000,
    )


def test_with_issues(user, milestone):
    """
    Test with issues.

    :param user:
    :param milestone:
    """
    IssueFactory.create_batch(
        3,
        user=user,
        milestone=milestone,
        total_time_spent=0,
    )

    checkers.check_milestone_metrics(
        get_milestone_metrics(milestone),
        budget=10000,
        profit=10000,
        budget_remains=10000,
        issues_count=3,
        issues_opened_count=3,
    )


def test_payrolls(user, milestone):
    """
    Test payrolls.

    :param user:
    :param milestone:
    """
    issues = [
        IssueFactory.create(user=user, milestone=milestone),
        IssueFactory.create(user=user, milestone=milestone),
        IssueFactory.create(user=user),
    ]

    IssueSpentTimeFactory.create(
        user=user,
        base=issues[0],
        time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issues[0],
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issues[1],
        time_spent=-seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issues[2],
        time_spent=seconds(hours=3),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(user=user, milestone=milestone),
        time_spent=seconds(hours=1),
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(
            user=user,
            milestone=ProjectMilestoneFactory(),
        ),
        time_spent=seconds(hours=10),
    )

    checkers.check_milestone_metrics(
        get_milestone_metrics(milestone),
        budget=10000,
        payroll=3000,
        profit=7000,
        budget_remains=9700,
        budget_spent=300,
        issues_count=2,
        issues_opened_count=2,
    )


def test_no_spents(user, milestone):
    """
    Test no spents.

    :param user:
    :param milestone:
    """
    IssueFactory.create_batch(2, user=user, milestone=milestone)
    IssueFactory.create(user=user)

    checkers.check_milestone_metrics(
        get_milestone_metrics(milestone),
        budget=10000,
        profit=10000,
        budget_remains=10000,
        issues_count=2,
        issues_opened_count=2,
    )


def test_payrolls_no_budget(db):
    """
    Test payrolls no budget.

    :param db:
    """
    checkers.check_milestone_metrics(
        get_milestone_metrics(ProjectMilestoneFactory.create(budget=0)),
    )
