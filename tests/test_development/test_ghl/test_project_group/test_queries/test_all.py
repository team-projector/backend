import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models.choices.project_state import ProjectState
from tests.test_development.factories import ProjectGroupFactory


def test_query(user, gql_client_authenticated, ghl_raw):
    """Test getting all project groups raw query."""
    ProjectGroupFactory.create_batch(3)

    response = gql_client_authenticated.execute(ghl_raw("all_project_groups"))

    assert "errors" not in response
    assert response["data"]["allProjectGroups"]["count"] == 3


def test_not_permissions(db, ghl_mock_info, all_project_groups_query):
    """Test permissions."""
    ProjectGroupFactory.create_batch(3)

    with pytest.raises(GraphQLPermissionDenied):
        all_project_groups_query(
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
    all_project_groups_query,
    state,
    count,
):
    """Test filtering by state param."""
    ProjectGroupFactory.create_batch(3, state=ProjectState.ARCHIVED)
    ProjectGroupFactory.create_batch(1, state=ProjectState.DEVELOPING)
    ProjectGroupFactory.create_batch(2, state=ProjectState.SUPPORTING)

    response = all_project_groups_query(
        root=None,
        info=ghl_auth_mock_info,
        state=state,
    )

    assert response.length == count
