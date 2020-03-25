# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLInputError
from apps.development.graphql.mutations.issues.inputs.add_spent import (
    ERROR_MSG_NO_GL_TOKEN,
)
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlProjectFactory,
)

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
    user.gl_token = "token"
    user.save()

    gl_project = GlProjectFactory.create()
    project = ProjectFactory.create(gl_id=gl_project["id"])

    gl_project_issue = GlIssueFactory.create(id=gl_project["id"])
    issue = IssueFactory.create(
        gl_iid=gl_project_issue["iid"], user=user, project=project,
    )

    IssueFactory.create_batch(5, project=project)
    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_ADD_SPENT_TO_ISSUE,
        variable_values={"id": issue.pk, "seconds": 60},
    )

    assert "errors" not in response

    dto = response["data"]["addSpendTimeIssue"]["issue"]
    assert dto["id"] == str(issue.id)


def test_user_without_gl_token(
    issue, ghl_auth_mock_info, add_spent_issue_mutation,
):
    with pytest.raises(GraphQLInputError) as exc_info:
        add_spent_issue_mutation(
            root=None, info=ghl_auth_mock_info, id=issue.id, seconds=60,
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "nonFieldErrors"
    assert extensions["fieldErrors"][0]["messages"][0] == ERROR_MSG_NO_GL_TOKEN


def test_bad_time(issue, user, ghl_auth_mock_info, add_spent_issue_mutation):
    user.gl_token = "token"
    user.save()

    with pytest.raises(GraphQLInputError) as exc_info:
        add_spent_issue_mutation(
            root=None, info=ghl_auth_mock_info, id=issue.id, seconds=-30,
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "seconds"
