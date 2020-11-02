import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models.project import ProjectState
from tests.test_development.factories import ProjectFactory

GHL_QUERY_ALL_PROJECTS = """
query ($state: ProjectState, $offset: Int, $first: Int) {
  allProjects(state: $state, offset: $offset, first: $first) {
    count
    edges {
      node {
        id
        title
      }
    }
  }
}
"""


def test_query(user, gql_client_authenticated):
    """Test getting all projects raw query."""
    ProjectFactory.create_batch(3)

    response = gql_client_authenticated.execute(GHL_QUERY_ALL_PROJECTS)

    assert "errors" not in response
    assert response["data"]["allProjects"]["count"] == 3


def test_not_permissions(db, ghl_mock_info, all_projects_query):
    """Test permissions."""
    ProjectFactory.create_batch(3)

    with pytest.raises(GraphQLPermissionDenied):
        all_projects_query(
            root=None,
            info=ghl_mock_info,
        )


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
        state=state,
    )

    assert response.length == count
