from datetime import datetime
from pytest import raises
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.development.graphql.mutations.ticket import (
    CreateTicketMutation,
    UpdateTicketMutation,
)
from apps.development.graphql.types.ticket import TicketType
from apps.development.models.ticket import (
    Ticket,
    TYPE_FEATURE,
    TYPE_BUG_FIXING,)

from tests.test_development.factories import (
    TicketFactory,
    ProjectMilestoneFactory
)
from tests.test_development.factories_gitlab import AttrDict


def test_ticket(user, client):
    ticket = TicketFactory.create()
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


def test_ticket_create(user, client):
    client.user = user
    info = AttrDict({'context': client})

    CreateTicketMutation.do_mutate(
        root=None,
        info=info,
        title='test ticket',
        type=TYPE_FEATURE,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='test1.com'
    )

    assert Ticket.objects.count() == 1

    ticket = Ticket.objects.first()
    assert ticket.type == TYPE_FEATURE
    assert ticket.start_date is not None
    assert ticket.due_date is not None


def test_ticket_create_invalid(user, client):
    client.user = user
    info = AttrDict({'context': client})

    with raises(ValidationError):
        CreateTicketMutation.do_mutate(
            root=None,
            info=info,
            title='test ticket',
            type='invalid type',
            start_date=str(datetime.now().date()),
            due_date=str(datetime.now().date()),
            url='invalid url'
        )


def test_ticket_create_not_pm(user, client):
    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        CreateTicketMutation.mutate(
            root=None,
            info=info,
            title='test ticket',
            type=TYPE_BUG_FIXING,
            start_date=str(datetime.now().date()),
            due_date=str(datetime.now().date()),
            url='test url'
        )

    user.roles.project_manager = True
    user.save()

    CreateTicketMutation.mutate(
        root=None,
        info=info,
        title='test ticket',
        type=TYPE_BUG_FIXING,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='test1.com'
    )


def test_ticket_update(user, client):
    client.user = user
    info = AttrDict({'context': client})

    ticket = TicketFactory.create(
        title='title created',
        type=TYPE_BUG_FIXING,
        url='http://created.test',
    )

    UpdateTicketMutation.do_mutate(
        root=None,
        info=info,
        id=ticket.id,
        title='updated',
        type=TYPE_FEATURE,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='http://updated.test',
    )

    assert Ticket.objects.count() == 1

    ticket.refresh_from_db()
    assert ticket.title == 'updated'
    assert ticket.start_date is not None
    assert ticket.due_date is not None
    assert ticket.url == 'http://updated.test'


def test_ticket_update_milestone(user, client):
    client.user = user
    info = AttrDict({'context': client})

    ticket = TicketFactory.create(milestone=ProjectMilestoneFactory.create())

    milestone = ProjectMilestoneFactory.create()

    UpdateTicketMutation.do_mutate(
        root=None,
        info=info,
        id=ticket.id,
        milestone=milestone.id
    )

    assert Ticket.objects.count() == 1
    assert Ticket.objects.first().milestone == milestone


def test_ticket_update_not_pm(user, client):
    ticket = TicketFactory.create()

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        UpdateTicketMutation.mutate(
            root=None,
            info=info,
            id=ticket.id,
        )

    user.roles.project_manager = True
    user.save()

    UpdateTicketMutation.mutate(
        root=None,
        info=info,
        id=ticket.id,
    )
