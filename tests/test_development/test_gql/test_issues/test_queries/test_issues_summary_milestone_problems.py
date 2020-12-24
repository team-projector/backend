import pytest

from apps.development.models.milestone import MilestoneState
from apps.development.models.project_member import ProjectMember
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)


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
    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.MANAGER,
        owner=milestone.owner,
    )
    IssueFactory.create_batch(
        5,
        user=user,
        project=milestone.owner,
        milestone=milestone,
    )

    response = gql_client_authenticated.execute(
        gql_raw("issues_summary_milestone_problems"),
        variable_values={"id": user.pk},
    )

    assert "errors" not in response
    assert response["data"]["issues"]["count"] == 5


def test_issues_summary_as_developer(
    user,
    gql_client_authenticated,
    gql_raw,
    milestone,
):
    """Test issues summary as developer."""
    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.DEVELOPER,
        owner=milestone.owner,
    )
    IssueFactory.create_batch(
        5,
        user=user,
        project=milestone.owner,
        milestone=milestone,
    )

    response = gql_client_authenticated.execute(
        gql_raw("issues_summary_milestone_problems"),
        variable_values={"id": user.pk},
    )

    assert "errors" in response
