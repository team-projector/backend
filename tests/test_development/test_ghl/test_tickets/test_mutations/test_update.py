from apps.development.models.ticket import Ticket, TicketState
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)


def test_query(project_manager, ghl_client, ticket, ghl_raw):
    """Test update ticket raw query."""
    ghl_client.set_user(project_manager)

    new_title = "new_{0}".format(ticket.title)
    response = ghl_client.execute(
        ghl_raw("update_ticket"),
        variable_values={
            "id": ticket.pk,
            "title": new_title,
            "state": TicketState.DOING,
        },
    )

    assert "errors" not in response

    dto = response["data"]["updateTicket"]["ticket"]
    assert dto["id"] == str(ticket.id)
    assert dto["title"] == new_title

    ticket.refresh_from_db()
    assert ticket.title == new_title


def test_attach_issues(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test attach issues."""
    attached_issue = IssueFactory(ticket=ticket, user=project_manager)
    issue = IssueFactory(user=project_manager)

    update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        attach_issues=[issue.id],
    )

    issue.refresh_from_db()

    assert ticket == attached_issue.ticket
    assert ticket == issue.ticket


def test_clear_issues(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test clear issues."""
    issue = IssueFactory(ticket=ticket, user=project_manager)

    update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        issues=[],
    )

    issue.refresh_from_db()
    assert not issue.ticket


def test_update_state(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test update state."""
    assert TicketState.CREATED == ticket.state

    update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        state=TicketState.PLANNING,
    )

    ticket.refresh_from_db()

    assert TicketState.PLANNING == ticket.state


def test_update_milestone(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test update milestone."""
    new_milestone = ProjectMilestoneFactory()
    update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        milestone=new_milestone.id,
    )

    ticket.refresh_from_db()

    assert new_milestone == ticket.milestone


def test_not_update_url(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test not update url."""
    ticket.url = "https://www.test.com"
    ticket.save()

    assert ticket.state == TicketState.CREATED

    update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        state=TicketState.PLANNING,
        url=None,
    )

    ticket.refresh_from_db()

    assert TicketState.PLANNING == ticket.state
    assert not ticket.url


def test_update_estimate(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test update estimate."""
    Ticket.objects.filter(id=ticket.pk).update(estimate=0)

    estimate = 111

    update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        state=TicketState.PLANNING,
        estimate=estimate,
    )

    ticket.refresh_from_db()

    assert ticket.estimate == estimate
