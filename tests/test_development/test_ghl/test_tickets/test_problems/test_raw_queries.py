from django.utils import timezone

from apps.development.services.ticket.problems import PROBLEM_OVER_DUE_DATE
from tests.test_development.factories import IssueFactory, TicketFactory


def test_list(user, ghl_client, ghl_raw):
    """Test getting all tickets with problems."""
    for ticket in TicketFactory.create_batch(5, due_date=timezone.now()):
        IssueFactory(
            ticket=ticket,
            user=user,
            due_date=timezone.now() + timezone.timedelta(days=1),
        )

    ghl_client.set_user(user)

    response = ghl_client.execute(ghl_raw("all_tickets"))

    assert "errors" not in response
    assert response["data"]["allTickets"]["count"] == 5

    for edge in response["data"]["allTickets"]["edges"]:
        assert edge["node"]["problems"] == [PROBLEM_OVER_DUE_DATE]


def test_retreive(user, ghl_client, ghl_raw):
    """Test getting ticket with problems."""
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
        user=user,
    )

    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw("ticket"),
        variable_values={"id": issue.ticket_id},
    )

    assert "errors" not in response
    assert response["data"]["ticket"]["problems"] == [PROBLEM_OVER_DUE_DATE]
