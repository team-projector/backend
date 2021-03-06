from django.utils import timezone

from apps.development.services.ticket.problems import PROBLEM_OVER_DUE_DATE
from tests.test_development.factories import IssueFactory, TicketFactory


def test_list(user, gql_client, gql_raw):
    """Test getting all tickets with problems."""
    for ticket in TicketFactory.create_batch(5, due_date=timezone.now()):
        IssueFactory(
            ticket=ticket,
            user=user,
            due_date=timezone.now() + timezone.timedelta(days=1),
        )

    gql_client.set_user(user)

    response = gql_client.execute(gql_raw("all_tickets"))

    assert "errors" not in response
    assert response["data"]["allTickets"]["count"] == 5

    for edge in response["data"]["allTickets"]["edges"]:
        assert edge["node"]["problems"] == [PROBLEM_OVER_DUE_DATE]


def test_retreive(user, gql_client, gql_raw):
    """Test getting ticket with problems."""
    issue = IssueFactory(
        ticket=TicketFactory(due_date=timezone.now()),
        due_date=timezone.now() + timezone.timedelta(days=1),
        user=user,
    )

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("ticket"),
        variable_values={"id": issue.ticket_id},
    )

    assert "errors" not in response
    assert response["data"]["ticket"]["problems"] == [PROBLEM_OVER_DUE_DATE]
