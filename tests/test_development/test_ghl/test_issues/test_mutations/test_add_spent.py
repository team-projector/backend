from pytest import raises

from apps.core.graphql.errors import GraphQLInputError
from apps.development.graphql.mutations.issues.inputs.add_spent import (
    ERROR_MSG_NO_GL_TOKEN,
)
from tests.helpers.objects import AttrDict
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories.gitlab import (
    GlIssueAddSpentTimeFactory,
    GlIssueFactory,
    GlProjectFactory,
)
from tests.test_users.factories.gitlab import GlUserFactory

GHL_QUERY_ADD_SPENT_TO_ISSUE = """
mutation (
    $id: ID!, $seconds: Int!
) {
addSpendTimeIssue(
    id: $id, seconds: $seconds
) {
    issue {
      id
      totalTimeSpent
      }
    }
  }
"""


def test_query(project_manager, ghl_client, gl_mocker, user):
    """Test add spent raw query."""
    user.gl_token = 'token'
    user.save()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_project_issue = AttrDict(GlIssueFactory(id=gl_project.id))
    issue = IssueFactory.create(
        gl_iid=gl_project_issue.iid,
        user=user,
        project=project,
    )

    IssueFactory.create_batch(5, project=project)

    gl_mocker.registry_get(
        '/user',
        GlUserFactory()
    )
    gl_mocker.registry_get(
        '/projects/{0}'.format(gl_project.id),
        gl_project
    )
    gl_mocker.registry_get(
        '/projects/{0}/issues/{1}'.format(
            gl_project.id,
            gl_project_issue.iid,
        ),
        gl_project_issue
    )

    time_spent = GlIssueAddSpentTimeFactory()
    gl_mocker.registry_post(
        '/projects/{0}/issues/{1}/add_spent_time'.format(
            gl_project.id,
            gl_project_issue.iid,
        ),
        time_spent)

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_ADD_SPENT_TO_ISSUE,
        variables={
            'id': issue.pk,
            'seconds': 60,
        }
    )

    assert 'errors' not in response

    dto = response['data']['addSpendTimeIssue']['issue']
    assert dto['id'] == str(issue.id)


def test_user_without_gl_token(
    issue,
    ghl_auth_mock_info,
    add_spent_issue_mutation
):
    with raises(GraphQLInputError) as exc_info:
        add_spent_issue_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=issue.id,
            seconds=60
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions['fieldErrors']) == 1
    assert extensions['fieldErrors'][0]['fieldName'] == 'nonFieldErrors'
    assert extensions['fieldErrors'][0]['messages'][0] == ERROR_MSG_NO_GL_TOKEN


def test_bad_time(
    issue,
    user,
    ghl_auth_mock_info,
    add_spent_issue_mutation
):
    user.gl_token = 'token'
    user.save()

    with raises(GraphQLInputError) as exc_info:
        add_spent_issue_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=issue.id,
            seconds=-30
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions['fieldErrors']) == 1
    assert extensions['fieldErrors'][0]['fieldName'] == 'seconds'
