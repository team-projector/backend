from apps.development.models import MergeRequest
from apps.development.models.merge_request import MergeRequestState
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory


def test_raw_query(  # noqa: WPS211
    project_manager,
    gql_client,
    gl_mocker,
    user,
    gl_client,
    gql_raw,
):
    """Test raw query."""
    merge_request = _prepare_sync_data(gl_mocker)

    assert merge_request.state == MergeRequestState.OPENED

    merge_request.state = MergeRequestState.CLOSED
    merge_request.save()

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("sync_merge_request"),
        variable_values={"id": merge_request.pk},
    )

    assert "errors" not in response
    merge_request.refresh_from_db()

    assert merge_request.state == MergeRequestState.OPENED


def _prepare_sync_data(gl_mocker) -> MergeRequest:
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

    return MergeRequest.objects.first()
