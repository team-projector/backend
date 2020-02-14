from django.utils import timezone

from apps.development.services.ticket.problems import PROBLEM_OVER_DUE_DATE
from tests.test_development.factories import IssueFactory, TicketFactory

GHL_QUERY_ALL_TICKETS = """
query {
  allTickets {
    count
    edges {
      node {
        id
        problems
      }
    }
  }
}
"""

GHL_QUERY_TICKET = """
query ($id: ID!) {
  ticket (id: $id) {
    id
    problems
  }
}
"""


def test_list(user, ghl_client):
    """Test getting all tickets with problems."""
    for ticket in TicketFactory.create_batch(5, due_date=timezone.now()):
        IssueFactory(
            ticket=ticket,
            due_date=timezone.now() + timezone.timedelta(days=1),
        )

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_ALL_TICKETS,
    )

    assert "errors" not in response
    assert response["data"]["allTickets"]["count"] == 5

    for edge in response["data"]["allTickets"]["edges"]:
        assert edge["node"]["problems"] == [PROBLEM_OVER_DUE_DATE]


def test_retreive(user, ghl_client):
    """Test getting ticket with problems."""
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
    )

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_TICKET,
        variable_values={
            "id": issue.ticket_id,
        },
    )

    assert "errors" not in response
    assert response["data"]["ticket"]["problems"] == [PROBLEM_OVER_DUE_DATE]
