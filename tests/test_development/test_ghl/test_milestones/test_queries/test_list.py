import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models.project_member import ProjectMemberRole
from tests.test_development.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)

GHL_QUERY_ALL_ISSUES = """
query {
  allMilestones {
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
    """Test getting all milestones raw query."""
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=ProjectMemberRole.MANAGER,
        owner=project,
    )
    ProjectMilestoneFactory.create_batch(5, owner=project)

    response = gql_client_authenticated.execute(GHL_QUERY_ALL_ISSUES)

    assert response["data"]["allMilestones"]["count"] == 5


def test_not_permissions(ghl_auth_mock_info, all_milestones_query):
    """Test permissions."""
    ProjectMilestoneFactory.create()

    with pytest.raises(GraphQLPermissionDenied):
        all_milestones_query(
            root=None,
            info=ghl_auth_mock_info,
        )


def test_search_by_title(ghl_auth_mock_info, all_milestones_query):
    """Test search by title."""
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=ghl_auth_mock_info.context.user,
        role=ProjectMemberRole.MANAGER,
        owner=project,
    )
    milestones = ProjectMilestoneFactory.create_batch(5, owner=project)

    milestone = milestones[0]

    milestone.title = "project_milestone"
    milestone.save()

    response = all_milestones_query(
        root=None,
        info=ghl_auth_mock_info,
        q="project_milestone",
    )

    assert response.length == 1
    assert response.edges[0].node.id == milestone.id


def test_search_by_gl_url(ghl_auth_mock_info, all_milestones_query):
    """Test search by gl_url."""
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=ghl_auth_mock_info.context.user,
        role=ProjectMemberRole.MANAGER,
        owner=project,
    )
    milestones = ProjectMilestoneFactory.create_batch(5, owner=project)

    milestone = milestones[0]

    milestone.gl_url = "https://gl.com/project/milestone"
    milestone.save()

    response = all_milestones_query(
        root=None,
        info=ghl_auth_mock_info,
        q="https://gl.com/project/milestone",
    )

    assert response.length == 1
    assert response.edges[0].node.id == milestone.id


def test_search_by_gl_url_not_full(ghl_auth_mock_info, all_milestones_query):
    """Test search by gl_url not full."""
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=ghl_auth_mock_info.context.user,
        role=ProjectMemberRole.MANAGER,
        owner=project,
    )
    milestones = ProjectMilestoneFactory.create_batch(5, owner=project)

    milestone = milestones[0]

    milestone.gl_url = "https://gl.com/project/milestone"
    milestone.save()

    response = all_milestones_query(
        root=None,
        info=ghl_auth_mock_info,
        q="https://gl.com/project/",
    )

    assert not response.length


def test_search_no_results(ghl_auth_mock_info, all_milestones_query):
    """Test search empty result."""
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=ghl_auth_mock_info.context.user,
        role=ProjectMemberRole.MANAGER,
        owner=project,
    )
    ProjectMilestoneFactory.create_batch(5, owner=project)

    response = all_milestones_query(
        root=None,
        info=ghl_auth_mock_info,
        q="example_query_search",
    )

    assert not response.length
