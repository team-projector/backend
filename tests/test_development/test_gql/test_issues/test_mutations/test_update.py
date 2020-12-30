from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_graphene_toolbox.errors.permission_denied import ACCESS_DENIED

from tests.test_development.factories import IssueFactory

KEY_ID = "id"


def test_query(issue, ticket, gql_client, user, gql_raw):
    """
    Test query.

    :param issue:
    :param ticket:
    :param gql_client:
    :param user:
    """
    assert issue.ticket is None

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("update_issue"),
        variable_values={KEY_ID: issue.pk, "ticket": ticket.pk},
    )

    assert "errors" not in response

    dto = response["data"]["updateIssue"]["issue"]
    assert dto[KEY_ID] == str(issue.id)
    assert dto["ticket"][KEY_ID] == str(ticket.id)

    issue.refresh_from_db()
    assert issue.ticket == ticket


def test_without_access(
    user,
    ghl_auth_mock_info,
    update_issue_mutation,
    ticket,
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
        root=None,
        info=ghl_auth_mock_info,
        id=issue.id,
        ticket=ticket.id,
    )

    assert isinstance(resolve, GraphQLPermissionDenied)
    assert resolve.extensions == {"code": ACCESS_DENIED}


def test_ticket_propagation(
    user,
    ghl_auth_mock_info,
    update_issue_mutation,
    ticket,
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
        user=user,
        ticket=None,
        description=child_issue.gl_url,
    )

    update_issue_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=issue.pk,
        ticket=ticket.id,
    )

    issue.refresh_from_db()
    child_issue.refresh_from_db()

    assert issue.ticket == child_issue.ticket
