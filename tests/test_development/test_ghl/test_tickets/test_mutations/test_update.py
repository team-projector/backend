# -*- coding: utf-8 -*-

from pytest import raises
from rest_framework.exceptions import PermissionDenied

from tests.test_development.factories import IssueFactory

GHL_QUERY_UPDATE_TICKET = """
mutation (
    $id: ID!, $attachIssues: [ID!], $type: String, $title: String,
    $role: String, $startDate: Date, $dueDate: Date, $url: String,
    $issues: [ID!]
) {
updateTicket(
    id: $id, attachIssues: $attachIssues, type: $type, title: $title,
    startDate: $startDate, dueDate: $dueDate, url: $url, issues: $issues,
    role: $role
) {
    errors{
      field
      messages
    }
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

    new_title = 'new_{0}'.format(ticket.title)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'id': ticket.pk,
            'title': new_title,
        }
    )

    assert 'errors' not in response
    assert not response['data']['updateTicket']['errors']

    dto = response['data']['updateTicket']['ticket']
    assert dto['id'] == str(ticket.id)
    assert dto['title'] == new_title

    ticket.refresh_from_db()
    assert ticket.title == new_title


def test_without_permissions(
    user,
    ghl_auth_mock_info,
    update_ticket_mutation,
    ticket,
):
    """Test non project manager."""
    with raises(PermissionDenied):
        update_ticket_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=ticket.id,
            title='new_{0}'.format(ticket.title),
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

    response = update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        attach_issues=[issue.id],
    )

    assert not response.errors

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

    response = update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.id,
        issues=[],
    )

    assert not response.errors

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
    response = update_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.pk,
        issues=[issue.pk],
        attach_issues=[issue.pk],
    )

    assert len(response.errors) == 1
    assert response.errors[0].field == 'non_field_errors'
