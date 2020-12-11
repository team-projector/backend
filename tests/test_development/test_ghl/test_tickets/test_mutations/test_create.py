from datetime import datetime

import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLInputError,
    GraphQLPermissionDenied,
)
from jnt_django_graphene_toolbox.errors.input import INPUT_ERROR

from apps.development.models.ticket import TicketState, TicketType
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)

TICKET_TITLE = "test ticket"


@pytest.fixture()
def ticket():
    """Ticket."""
    return TicketFactory(milestone=ProjectMilestoneFactory())


def test_query(project_manager, ghl_client, ghl_raw):
    """Test create ticket raw query."""
    ghl_client.set_user(project_manager)

    milestone = ProjectMilestoneFactory()

    issues = IssueFactory.create_batch(size=2, user=project_manager)

    response = ghl_client.execute(
        ghl_raw("create_ticket"),
        variable_values={
            "title": TICKET_TITLE,
            "type": TicketType.FEATURE,
            "startDate": str(datetime.now().date()),
            "dueDate": str(datetime.now().date()),
            "url": "http://test1.com",
            "milestone": str(milestone.id),
            "issues": [str(issue.pk) for issue in issues],
            "role": "Manager",
            "state": TicketState.DOING,
            "estimate": None,
        },
    )

    assert "errors" not in response

    dto = response["data"]["createTicket"]["ticket"]
    assert dto["title"] == TICKET_TITLE

    for issue in issues:
        issue.refresh_from_db()
        assert issue.ticket_id == int(dto["id"])


def test_invalid_parameters(
    project_manager,
    ghl_auth_mock_info,
    create_ticket_mutation,
):
    """Test creation with invalid parameters."""
    resolve = create_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        title=TICKET_TITLE,
        type="invalid type",
        url="invalid url",
        milestone="",
        state="invalid state",
    )

    isinstance(resolve, GraphQLInputError)

    extensions = resolve.extensions
    assert extensions["code"] == INPUT_ERROR

    fields_with_errors = {
        err["fieldName"] for err in extensions["fieldErrors"]
    }

    assert fields_with_errors == {"url", "type", "milestone", "state"}


def test_without_permissions(user, ghl_auth_mock_info, create_ticket_mutation):
    """Test deletion without permissions."""
    milestone = ProjectMilestoneFactory()

    resolve = create_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        title=TICKET_TITLE,
        startDate=datetime.now().date(),
        dueDate=datetime.now().date(),
        type=TicketType.FEATURE,
        url="http://test1.com",
        milestone=milestone.pk,
    )

    isinstance(resolve, GraphQLPermissionDenied)


def test_role_url_is_null(
    project_manager,
    ghl_auth_mock_info,
    create_ticket_mutation,
):
    """Test if url and/or role is none."""
    resolve = create_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        title=TICKET_TITLE,
        type=TicketType.FEATURE,
        state=TicketState.DOING,
        milestone=ProjectMilestoneFactory.create().id,
        url=None,
        role=None,
    )

    ticket = resolve.ticket
    assert ticket.title == TICKET_TITLE
    assert not ticket.url
    assert not ticket.role
