import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models.project import ProjectState
from tests.test_development.factories import ProjectFactory


def test_query(user, gql_client_authenticated, gql_raw):
    """Test getting all projects raw query."""
    ProjectFactory.create_batch(3)

    response = gql_client_authenticated.execute(gql_raw("all_projects"))

    assert "errors" not in response
    assert response["data"]["allProjects"]["count"] == 3


def test_unauth(db, ghl_mock_info, all_projects_query):
    """Test permissions."""
    ProjectFactory.create_batch(3)

    response = all_projects_query(
        root=None,
        info=ghl_mock_info,
    )

    assert isinstance(response, GraphQLPermissionDenied)


@pytest.mark.parametrize(
    ("state", "count"),
    [
        (ProjectState.ARCHIVED, 3),
        (ProjectState.DEVELOPING, 1),
        (ProjectState.SUPPORTING, 2),
    ],
)
def test_filter_by_state(
    ghl_auth_mock_info,
    all_projects_query,
    state,
    count,
):
    """Test filtering by state param."""
    ProjectFactory.create_batch(3, state=ProjectState.ARCHIVED)
    ProjectFactory.create_batch(1, state=ProjectState.DEVELOPING)
    ProjectFactory.create_batch(2, state=ProjectState.SUPPORTING)

    response = all_projects_query(
        root=None,
        info=ghl_auth_mock_info,
        state=[state],
    )

    assert response.length == count
