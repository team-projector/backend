import pytest

from apps.development.models.ticket import TicketState
from tests.test_development.factories import TicketFactory

GHL_QUERY_TICKETS_SUMMARY = """
query {
    ticketsSummary {
        count
        createdCount
        planningCount
        doingCount
        testingCount
        acceptingCount
        doneCount
    }
}
"""


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


def test_raw_query(ghl_client, tickets):
    """
    Test raw query.

    :param ghl_client:
    :param tickets:
    """
    response = ghl_client.execute(GHL_QUERY_TICKETS_SUMMARY)

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
