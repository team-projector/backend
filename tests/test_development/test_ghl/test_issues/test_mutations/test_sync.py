from pytest import raises

from apps.core.graphql.errors import GraphQLInputError
from apps.development.models.issue import ISSUE_STATES
from tests.helpers.objects import AttrDict
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlProjectFactory,
    GlTimeStats,
)
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
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_assignee = AttrDict(GlUserFactory())
    UserFactory.create(gl_id=gl_assignee.id)

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id,
        assignee=gl_assignee,
        state='closed'
    ))

    issue = IssueFactory.create(
        user=user,
        gl_id=gl_issue.id,
        gl_iid=gl_issue.iid,
        project=project,
        state='opened'
    )

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
        gl_issue
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats',
        GlTimeStats()
    )
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', []
    )
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', []
    )

    assert issue.state == 'opened'

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_SYNC_ISSUE,
        variables={
            'id': issue.pk,
        }
    )

    assert 'errors' not in response

    dto = response['data']['syncIssue']['issue']
    assert dto['id'] == str(issue.id)

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
    assert len(extensions['fieldErrors']) == 1
    assert extensions['fieldErrors'][0]['fieldName'] == 'id'
