import pytest

from apps.development.graphql.mutations.ticket import DeleteTicketMutation
from apps.development.graphql.types.ticket import TicketType
from apps.development.models.ticket import Ticket
from tests.test_development.factories import TicketFactory
from tests.test_development.factories_gitlab import AttrDict


@pytest.fixture()
def project_manager(user):
    user.roles.PROJECT_MANAGER = True
    user.save()
    return user


def test_ticket(user, client):
    ticket = TicketFactory()
    TicketFactory.create_batch(3)

    client.user = user
    info = AttrDict({'context': client})

    assert TicketType().get_node(info, ticket.id) == ticket


def test_tickets(user, client):
    TicketFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    tickets = TicketType().get_queryset(Ticket.objects.all(), info)

    assert tickets.count() == 5


def test_delete_ticket(user, client):
    user.roles.PROJECT_MANAGER = True
    user.save()

    ticket = TicketFactory()

    client.user = user
    info = AttrDict({'context': client})

    assert Ticket.objects.count() == 1

    DeleteTicketMutation.mutate(
        None,
        info,
        id=ticket.id,
    )

    assert Ticket.objects.count() == 0
