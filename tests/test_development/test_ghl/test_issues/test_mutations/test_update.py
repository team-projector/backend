# -*- coding: utf-8 -*-

from jnt_django_graphene_toolbox.errors import GraphQLInputError

from tests.test_development.factories import IssueFactory

GHL_QUERY_UPDATE_ISSUE = """
mutation (
    $id: ID!, $ticket: ID!
) {
updateIssue(
    id: $id, ticket: $ticket
) {
    issue {
      id
      ticket {
        id
        }
      }
    }
  }
"""


def test_query(issue, ticket, ghl_client, user):
    """
    Test query.

    :param issue:
    :param ticket:
    :param ghl_client:
    :param user:
    """
    assert issue.ticket is None

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_ISSUE,
        variable_values={"id": issue.pk, "ticket": ticket.pk},
    )

    assert "errors" not in response

    dto = response["data"]["updateIssue"]["issue"]
    assert dto["id"] == str(issue.id)
    assert dto["ticket"]["id"] == str(ticket.id)

    issue.refresh_from_db()
    assert issue.ticket == ticket


def test_without_access(
    user, ghl_auth_mock_info, update_issue_mutation, ticket,
):
    """
    Test without access.

    :param user:
    :param ghl_auth_mock_info:
    :param update_issue_mutation:
    :param ticket:
    """
    issue = IssueFactory.create()

    resolve = update_issue_mutation(
        root=None, info=ghl_auth_mock_info, id=issue.id, ticket=ticket.id,
    )

    assert isinstance(resolve, GraphQLInputError)

    extensions = resolve.extensions
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "id"


def test_ticket_propagation(
    user, ghl_auth_mock_info, update_issue_mutation, ticket,
):
    """
    Test ticket propagation.

    :param user:
    :param ghl_auth_mock_info:
    :param update_issue_mutation:
    :param ticket:
    """
    child_issue = IssueFactory.create(
        ticket=None,
        gl_url="https://gitlab.com/junte/team-projector/backend/issues/12",
    )
    issue = IssueFactory.create(
        user=user, ticket=None, description=child_issue.gl_url,
    )

    update_issue_mutation(
        root=None, info=ghl_auth_mock_info, id=issue.pk, ticket=ticket.id,
    )

    child_issue.refresh_from_db()

    assert issue.ticket == child_issue.ticket
