import pytest

from apps.development.models.ticket import TicketState
from tests.test_development.factories import TicketFactory


@pytest.fixture()
def tickets(db):
    """
    Tickets.

    :param db:
    """
    return (
        TicketFactory.create(state=TicketState.TESTING),
        TicketFactory.create(state=TicketState.ACCEPTING),
        TicketFactory.create(state=TicketState.DONE),
    )


def test_raw_query(gql_client_authenticated, tickets, gql_raw):
    """
    Test raw query.

    :param gql_client_authenticated:
    :param tickets:
    """
    response = gql_client_authenticated.execute(gql_raw("tickets_summary"))

    assert "errors" not in response

    dto = response["data"]["ticketsSummary"]
    assert dto == {
        "count": 3,
        "createdCount": 0,
        "planningCount": 0,
        "doingCount": 0,
        "testingCount": 1,
        "acceptingCount": 1,
        "doneCount": 1,
    }


def test_filter_by_milestone(
    tickets_summary_query,
    ghl_auth_mock_info,
    tickets,
):
    """
    Test filter by milestone.

    :param tickets_summary_query:
    :param ghl_auth_mock_info:
    :param tickets:
    """
    response = tickets_summary_query(
        parent=None,
        root=None,
        info=ghl_auth_mock_info,
        milestone=tickets[0].milestone.id,
    )

    assert response == {
        "count": 1,
        "created_count": 0,
        "planning_count": 0,
        "doing_count": 0,
        "testing_count": 1,
        "accepting_count": 0,
        "done_count": 0,
    }
