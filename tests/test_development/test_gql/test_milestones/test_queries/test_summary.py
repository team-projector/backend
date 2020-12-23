import pytest

from apps.development.models.milestone import MilestoneState
from apps.development.models.project_member import ProjectMember
from apps.users.models import User
from tests.test_development.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)


@pytest.fixture()
def milestones(user):
    """
    Milestones.

    :param user:
    """
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        roles=ProjectMember.roles.MANAGER,
        owner=project,
    )
    return (
        ProjectMilestoneFactory.create(
            state=MilestoneState.ACTIVE,
            owner=project,
        ),
        ProjectMilestoneFactory.create(
            state=MilestoneState.CLOSED,
            owner=project,
        ),
    )


def test_raw_query(user, gql_client_authenticated, milestones, ghl_raw):
    """
    Test raw query.

    :param gql_client_authenticated:
    :param milestones:
    """
    user.roles = User.roles.DEVELOPER
    user.save()

    response = gql_client_authenticated.execute(ghl_raw("milestones_summary"))

    assert "errors" not in response

    dto = response["data"]["milestonesSummary"]
    assert dto == {"count": 2, "activeCount": 1, "closedCount": 1}


def test_filter_by_state(
    milestones_summary_query,
    ghl_auth_mock_info,
    milestones,
):
    """
    Test filter by state.

    :param milestones_summary_query:
    :param ghl_auth_mock_info:
    :param milestones:
    """
    response = milestones_summary_query(
        parent=None,
        root=None,
        info=ghl_auth_mock_info,
        state=MilestoneState.ACTIVE,
    )

    assert response == {"count": 1, "active_count": 1, "closed_count": 0}
