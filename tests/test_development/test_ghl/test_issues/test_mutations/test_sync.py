from pytest import raises

from apps.core.graphql.errors import GraphQLInputError
from apps.development.models.issue import ISSUE_STATES
from tests.test_development.factories import IssueFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.factories.user import UserFactory

GHL_QUERY_SYNC_ISSUE = """
mutation (
    $id: ID!
) {
syncIssue(
    id: $id
) {
    issue {
      id
      state
      glIid
      }
    }
  }
"""


def test_query(project_manager, ghl_client, gl_mocker, user):
    project, gl_project = initializers.init_project()

    gl_assignee = GlUserFactory.create()
    UserFactory.create(gl_id=gl_assignee["id"])

    issue, gl_issue = initializers.init_issue(
        project,
        gl_project,
        model_kwargs={
            "user": user,
            "state": ISSUE_STATES.OPENED,
        },
        gl_kwargs={
            "assignee": gl_assignee,
            "state": "closed",
        },
    )

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_issue_endpoints(gl_mocker, gl_project, gl_issue)
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        issues=[gl_issue],
    )

    assert issue.state == ISSUE_STATES.OPENED

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_SYNC_ISSUE,
        variables={
            "id": issue.pk,
        }
    )

    assert "errors" not in response

    dto = response["data"]["syncIssue"]["issue"]
    assert dto["id"] == str(issue.id)

    issue.refresh_from_db()
    assert issue.state == ISSUE_STATES.CLOSED


def test_without_access(
    user,
    ghl_auth_mock_info,
    sync_issue_mutation,
):
    issue = IssueFactory()

    with raises(GraphQLInputError) as exc_info:
        sync_issue_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=issue.id,
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "id"
