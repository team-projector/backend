from datetime import datetime
from pytest import raises
from django.core.exceptions import PermissionDenied

from apps.development.graphql.mutations.ticket import (
    CreateTicketMutation, UpdateTicketMutation
)
from apps.development.graphql.types.ticket import TicketType
from apps.development.models.ticket import Ticket, TYPE_FEATURE, TYPE_BUG_FIXING
from apps.users.models import User
from tests.test_development.factories import (
    TicketFactory, ProjectMilestoneFactory
)
from tests.test_development.factories_gitlab import AttrDict


def test_tickets(user, client):
    user.roles = User.roles.project_manager
    user.save()

    TicketFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    tickets = TicketType().get_queryset(Ticket.objects.all(), info)

    assert tickets.count() == 5


def test_tickets_not_pm(user, client):
    TicketFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        TicketType().get_queryset(
            Ticket.objects.all(), info
        )


def test_ticket_create(user, client):
    user.roles = User.roles.project_manager
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    milestone = ProjectMilestoneFactory.create()

    CreateTicketMutation.do_mutate(
        None,
        info,
        title='test ticket',
        type=TYPE_FEATURE,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        milestone=milestone.id
    )

    assert Ticket.objects.count() == 1

    ticket = Ticket.objects.first()
    assert ticket.milestone == milestone
    assert ticket.type == TYPE_FEATURE
    assert ticket.start_date is not None
    assert ticket.due_date is not None


def test_ticket_update(user, client):
    user.roles = User.roles.project_manager
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    ticket = TicketFactory.create(type=TYPE_BUG_FIXING,
                                  milestone=ProjectMilestoneFactory.create())

    milestone = ProjectMilestoneFactory.create()

    UpdateTicketMutation.do_mutate(
        None,
        info,
        ticket.id,
        type=TYPE_FEATURE,
        milestone=milestone.id
    )

    assert Ticket.objects.count() == 1
    assert Ticket.objects.first().type == TYPE_FEATURE
    assert Ticket.objects.first().milestone == milestone
