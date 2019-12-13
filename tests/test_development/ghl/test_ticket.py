from datetime import datetime

import pytest
from pytest import raises
from rest_framework.exceptions import PermissionDenied

from apps.development.graphql.mutations.ticket import (
    CreateTicketMutation,
    DeleteTicketMutation,
    UpdateTicketMutation,
)
from apps.development.graphql.serializers.ticket import ISSUES_PARAM_ERROR
from apps.development.graphql.types.ticket import TicketType
from apps.development.models.ticket import (
    TYPE_BUG_FIXING,
    TYPE_FEATURE,
    Ticket,
)
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)
from tests.test_development.factories_gitlab import AttrDict


@pytest.fixture()
def project_manager(user):
    user.roles.PROJECT_MANAGER = True
    user.save()
    yield user


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


def test_ticket_create(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})
    iss_1, iss_2 = IssueFactory.create_batch(size=2, user=project_manager)

    result = CreateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        title='test ticket',
        type=TYPE_FEATURE,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='http://test1.com',
        issues=[iss_1.id, iss_2.id]
    )
    assert not result.errors
    assert Ticket.objects.count() == 1

    ticket = Ticket.objects.first()
    assert ticket.type == TYPE_FEATURE
    assert ticket.start_date is not None
    assert ticket.due_date is not None

    iss_1.refresh_from_db()
    iss_2.refresh_from_db()
    assert iss_1.ticket == ticket
    assert iss_2.ticket == ticket


def test_ticket_create_invalid(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})

    result = CreateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        title='test ticket',
        type='invalid type',
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='invalid url'
    )

    assert {'url', 'type'} == {err.field for err in result.errors}


def test_ticket_create_not_pm(user, client):
    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        CreateTicketMutation.mutate_and_get_payload(
            root=None,
            info=info,
            title='test ticket',
            type=TYPE_BUG_FIXING,
            start_date=str(datetime.now().date()),
            due_date=str(datetime.now().date()),
            url='test url'
        )

    user.roles.PROJECT_MANAGER = True
    user.save()

    CreateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        title='test ticket',
        type=TYPE_BUG_FIXING,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='test1.com'
    )


def test_ticket_update(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})

    ticket = TicketFactory(
        title='title created',
        type=TYPE_BUG_FIXING,
        url='http://created.test',
    )
    iss_1, iss_2 = IssueFactory.create_batch(size=2, user=project_manager)

    UpdateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        id=ticket.id,
        title='updated',
        type=TYPE_FEATURE,
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        url='http://updated.test',
        issues=[iss_1.id, iss_2.id]
    )

    assert Ticket.objects.count() == 1

    ticket.refresh_from_db()
    assert ticket.title == 'updated'
    assert ticket.start_date is not None
    assert ticket.due_date is not None
    assert ticket.url == 'http://updated.test'

    iss_1.refresh_from_db()
    iss_2.refresh_from_db()
    assert iss_1.ticket == ticket
    assert iss_2.ticket == ticket


def test_ticket_update_milestone(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})

    ticket = TicketFactory(milestone=ProjectMilestoneFactory.create())

    milestone = ProjectMilestoneFactory.create()

    UpdateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        id=ticket.id,
        milestone=milestone.id
    )

    assert Ticket.objects.count() == 1
    assert Ticket.objects.first().milestone == milestone


def test_ticket_attach_issues(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})

    ticket = TicketFactory()
    iss_1 = IssueFactory(ticket=ticket, user=project_manager)
    iss_2 = IssueFactory(user=project_manager)

    result = UpdateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        id=ticket.id,
        attach_issues=[iss_2.id]
    )

    assert not result.errors
    iss_1.refresh_from_db()
    iss_2.refresh_from_db()
    assert ticket == iss_1.ticket
    assert ticket == iss_2.ticket


def test_ticket_clear_issues(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})

    ticket = TicketFactory()
    issue = IssueFactory(ticket=ticket, user=project_manager)

    result = UpdateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        id=ticket.id,
        issues=[]
    )

    assert not result.errors
    issue.refresh_from_db()
    assert not issue.ticket


def test_ticket_both_params_attach_and_issues(project_manager, client):
    client.user = project_manager
    info = AttrDict({'context': client})

    ticket = TicketFactory()
    iss_1 = IssueFactory(user=project_manager)

    result = UpdateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        id=ticket.id,
        attach_issues=[iss_1.id],
        issues=[iss_1.id],
    )

    assert result.errors[0].field == 'non_field_errors'
    assert result.errors[0].messages[0] == ISSUES_PARAM_ERROR


def test_ticket_update_not_pm(user, client):
    ticket = TicketFactory()

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        UpdateTicketMutation.mutate_and_get_payload(
            root=None,
            info=info,
            id=ticket.id,
        )

    user.roles.PROJECT_MANAGER = True
    user.save()

    UpdateTicketMutation.mutate_and_get_payload(
        root=None,
        info=info,
        id=ticket.id,
    )


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
