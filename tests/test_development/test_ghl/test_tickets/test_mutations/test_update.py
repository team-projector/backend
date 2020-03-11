# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLInputError, GraphQLPermissionDenied
from apps.development.models.ticket import TicketState
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)

GHL_QUERY_UPDATE_TICKET = """
mutation (
    $id: ID!, $attachIssues: [ID!], $type: String, $title: String,
    $role: String, $startDate: Date, $dueDate: Date, $url: String,
    $issues: [ID!], $state: String!
) {
updateTicket(
    id: $id, attachIssues: $attachIssues, type: $type, title: $title,
    startDate: $startDate, dueDate: $dueDate, url: $url, issues: $issues,
    role: $role, state: $state
) {
    ticket {
      id
      title
      }
    }
  }
"""


def test_query(project_manager, ghl_client, ticket):
    """Test update ticket raw query."""
    ghl_client.set_user(project_manager)

    new_title = "new_{0}".format(ticket.title)
    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variable_values={
            "id": ticket.pk,
            "title": new_title,
            "state": TicketState.DOING,
        }
    )

    assert "errors" not in response

    dto = response["data"]["updateTicket"]["ticket"]
    assert dto["id"] == str(ticket.id)
    assert dto["title"] == new_title

    ticket.refresh_from_db()
    assert ticket.title == new_title


def test_without_permissions(
    user,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test non project manager."""
    with pytest.raises(GraphQLPermissionDenied):
        update_ticket_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=ticket.id,
            title="new_{0}".format(ticket.title),
        )


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


def test_both_params_attach_and_issues(
    project_manager,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test both attach and rewrite issues."""
    issue = IssueFactory(user=project_manager)

    with pytest.raises(GraphQLInputError) as exc_info:
        update_ticket_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=ticket.pk,
            issues=[issue.pk],
            attach_issues=[issue.pk],
        )

    extensions = exc_info.value.extensions  # noqa: WPS441
    assert len(extensions["fieldErrors"]) == 1
    assert extensions["fieldErrors"][0]["fieldName"] == "nonFieldErrors"


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
