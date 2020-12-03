from jnt_django_graphene_toolbox.errors import GraphQLInputError

from apps.development.services.errors import NoPersonalGitLabToken
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlProjectFactory,
)


def test_query(project_manager, ghl_client, gl_mocker, user, ghl_raw):
    """Test add spent raw query."""
    user.gl_token = "token"
    user.save()

    gl_project = GlProjectFactory.create()
    project = ProjectFactory.create(gl_id=gl_project["id"])

    gl_project_issue = GlIssueFactory.create(id=gl_project["id"])
    issue = IssueFactory.create(
        gl_iid=gl_project_issue["iid"],
        user=user,
        project=project,
    )

    IssueFactory.create_batch(5, project=project)
    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw("add_spend_time_issue"),
        variable_values={"id": issue.pk, "seconds": 60},
    )

    assert "errors" not in response

    dto = response["data"]["addSpendTimeIssue"]["issue"]
    assert dto["id"] == str(issue.id)


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
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "nonFieldErrors"
    assert (
        extensions["fieldErrors"][0]["messages"][0]
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
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "seconds"
