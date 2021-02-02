from datetime import datetime, timedelta

import pytest

from apps.development.models import Issue, ProjectMember
from apps.development.models.milestone import MilestoneState
from apps.users.models import User
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)
from tests.test_users.factories import UserFactory


@pytest.fixture()
def project(db):
    """Create project."""
    return ProjectFactory.create()


@pytest.fixture()
def milestone(project):
    """Create project."""
    return ProjectMilestoneFactory.create(
        owner=project,
        state=MilestoneState.ACTIVE,
    )


def test_issues_summary_query(
    user,
    gql_client_authenticated,
    gql_raw,
    milestone,
):
    """Test getting issues summary raw query."""
    user.roles = User.roles.DEVELOPER
    user.save()

    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.DEVELOPER,
        owner=milestone.owner,
    )
    today = datetime.now().date()

    _create_issues(
        user,
        {
            "project": milestone.owner,
            "milestone": milestone,
        },
        today,
    )

    response = gql_client_authenticated.execute(
        gql_raw("issues_summary_user_issues_summary"),
        variable_values={
            "assignedTo": user.pk,
            "dueDate": today,
        },
    )

    assert "errors" not in response

    _assert_issues_summary(response["data"]["summary"])
    _assert_user_issues_summary(response["data"]["user"], user, today)


def _create_issues(user, issue_data, due_date) -> None:
    """Prepare test data."""
    user1 = UserFactory.create()
    assignee1 = IssueFactory.create(user=user, due_date=due_date, **issue_data)
    assignee1.participants.add(user)

    assignee2 = IssueFactory.create(
        user=user,
        due_date=due_date + timedelta(days=1),
        **issue_data,
    )
    assignee2.participants.add(user, user1)

    IssueFactory.create(user=user, due_date=due_date, **issue_data)

    participant = IssueFactory.create(
        user=user,
        due_date=due_date - timedelta(days=1),
        **issue_data,
    )
    participant.participants.add(user)

    issue = IssueFactory.create(**issue_data, user=user, due_date=due_date)
    issue.participants.add(user, user1)


def _assert_issues_summary(issues_summary) -> None:
    """Assert issues summary."""
    assert issues_summary["count"] == 3
    assert issues_summary["openedCount"] == 3
    assert not issues_summary["closedCount"]
    assert not issues_summary["problemsCount"]


def _assert_user_issues_summary(user_issues_summary, user, due_date) -> None:
    """Assert user issues summary."""
    issues = Issue.objects.filter(due_date=due_date)
    issues_summary = user_issues_summary["issuesSummary"]

    assert issues_summary["assignedCount"] == issues.filter(user=user).count()
    assert issues_summary["createdCount"] == issues.filter(author=user).count()
    assert (
        issues_summary["participationCount"]
        == issues.filter(participants=user).count()
    )
