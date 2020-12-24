import pytest
from jnt_django_graphene_toolbox.errors import GraphQLInputError

from apps.development.services.errors import NoPersonalGitLabToken
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlProjectFactory,
)

FIELD_FIELD_ERRORS = "fieldErrors"
KEY_ID = "id"


@pytest.fixture()
def gl_project(db):
    """Create Gitlab fake project."""
    return GlProjectFactory.create()


def test_query(project_manager, gql_client, gl_mocker, gql_raw, gl_project):
    """Test add spent raw query."""
    project_manager.gl_token = "token"
    project_manager.save()

    project = ProjectFactory.create(gl_id=gl_project[KEY_ID])

    gl_project_issue = GlIssueFactory.create(id=gl_project[KEY_ID])
    issue = IssueFactory.create(
        gl_iid=gl_project_issue["iid"],
        user=project_manager,
        project=project,
    )

    IssueFactory.create_batch(5, project=project)
    gql_client.set_user(project_manager)

    response = gql_client.execute(
        gql_raw("add_spend_time_issue"),
        variable_values={KEY_ID: issue.pk, "seconds": 60},
    )

    assert "errors" not in response

    dto = response["data"]["addSpendTimeIssue"]["issue"]
    assert dto[KEY_ID] == str(issue.id)


def test_user_without_gl_token(
    issue,
    ghl_auth_mock_info,
    add_spent_issue_mutation,
):
    """
    Test user without gl token.

    :param issue:
    :param ghl_auth_mock_info:
    :param add_spent_issue_mutation:
    """
    resolve = add_spent_issue_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=issue.id,
        seconds=60,
    )

    isinstance(resolve, GraphQLInputError)

    extensions = resolve.extensions  # noqa: WPS441
    assert len(extensions[FIELD_FIELD_ERRORS]) == 1
    assert extensions[FIELD_FIELD_ERRORS][0]["fieldName"] == "nonFieldErrors"
    assert (
        extensions[FIELD_FIELD_ERRORS][0]["messages"][0]
        == NoPersonalGitLabToken.default_detail
    )


def test_bad_time(issue, user, ghl_auth_mock_info, add_spent_issue_mutation):
    """
    Test bad time.

    :param issue:
    :param user:
    :param ghl_auth_mock_info:
    :param add_spent_issue_mutation:
    """
    user.gl_token = "token"
    user.save()

    resolve = add_spent_issue_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=issue.id,
        seconds=-30,
    )

    isinstance(resolve, GraphQLInputError)

    extensions = resolve.extensions  # noqa: WPS441
    assert len(extensions[FIELD_FIELD_ERRORS]) == 1
    assert extensions[FIELD_FIELD_ERRORS][0]["fieldName"] == "seconds"
