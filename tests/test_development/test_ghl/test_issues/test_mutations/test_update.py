from pytest import raises

from apps.core.graphql.errors import GraphQLInputError
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
    assert issue.ticket is None

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_ISSUE,
        variables={
            "id": issue.pk,
            "ticket": ticket.pk,
        }
    )

    assert "errors" not in response

    dto = response["data"]["updateIssue"]["issue"]
    assert dto["id"] == str(issue.id)
    assert dto["ticket"]["id"] == str(ticket.id)

    issue.refresh_from_db()
    assert issue.ticket == ticket


def test_without_access(
    user,
    ghl_auth_mock_info,
    update_issue_mutation,
    ticket,
):
    issue = IssueFactory()

    with raises(GraphQLInputError) as exc_info:
        update_issue_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=issue.id,
            ticket=ticket.id,
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "id"
