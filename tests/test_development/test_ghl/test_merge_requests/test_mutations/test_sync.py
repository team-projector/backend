from jnt_django_graphene_toolbox.errors import GraphQLInputError

from apps.development.models import MergeRequest
from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.factories import IssueFactory
from tests.test_development.factories.gitlab import GlLabelFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory

GHL_QUERY_SYNC_MERGE_REQUEST = """
mutation ($id: ID!) {
  response: syncMergeRequest(id: $id) {
    mergeRequest {
      id
      glUrl
    }
  }
}
"""


def test_raw_query(project_manager, ghl_client, gl_mocker, user, gl_client):
    """Test raw query."""
    gl_assignee = GlUserFactory.create()
    UserFactory.create(gl_id=gl_assignee["id"])

    project, gl_project = initializers.init_project()

    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"assignee": gl_assignee, "state": MergeRequestState.OPENED},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request.state == MergeRequestState.OPENED

    merge_request.state = MergeRequestState.CLOSED
    merge_request.save()

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_SYNC_MERGE_REQUEST,
        variable_values={"id": merge_request.pk},
    )

    assert "errors" not in response
    merge_request.refresh_from_db()

    assert merge_request.state == MergeRequestState.OPENED
