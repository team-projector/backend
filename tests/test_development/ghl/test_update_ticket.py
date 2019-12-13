# -*- coding: utf-8 -*-

import pytest

from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)

GHL_QUERY_UPDATE_TICKET = """
mutation ($input: UpdateTicketMutationInput!) {
  updateTicket(input: $input) {
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


@pytest.fixture()
def project_manager(user):
    user.roles.PROJECT_MANAGER = True
    user.save()
    return user


@pytest.fixture()
def ticket():
    return TicketFactory(milestone=ProjectMilestoneFactory())


def test_success(project_manager, ghl_client, ticket):
    ghl_client.set_user(project_manager)
    new_title = 'new_{0}'.format(ticket.title)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'input': {
                'id': str(ticket.id),
                'title': new_title,
            }
        }
    )

    assert 'errors' not in response
    assert not response['data']['updateTicket']['errors']

    dto = response['data']['updateTicket']['ticket']
    assert dto['id'] == str(ticket.id)
    assert dto['title'] == new_title

    ticket.refresh_from_db()
    assert ticket.title == new_title


def test_without_permissions(user, ghl_client, ticket):
    ghl_client.set_user(user)
    new_title = 'new_{0}'.format(ticket.title)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'input': {
                'id': str(ticket.id),
                'title': new_title,
            }
        }
    )

    assert 'errors' in response


def test_update_milestone(project_manager, ghl_client, ticket):
    ghl_client.set_user(project_manager)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'input': {
                'id': str(ticket.id),
                'milestone': str(ProjectMilestoneFactory().id),
            }
        }
    )

    assert 'errors' in response


def test_attach_issues(project_manager, ghl_client, ticket):
    iss_1 = IssueFactory(ticket=ticket, user=project_manager)
    iss_2 = IssueFactory(user=project_manager)

    ghl_client.set_user(project_manager)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'input': {
                'id': str(ticket.id),
                'attachIssues': [str(iss_2.id)],
            }
        }
    )

    assert 'errors' not in response
    assert not response['data']['updateTicket']['errors']

    iss_1.refresh_from_db()
    iss_2.refresh_from_db()
    assert ticket == iss_1.ticket
    assert ticket == iss_2.ticket


def test_clear_issues(project_manager, ghl_client, ticket):
    issue = IssueFactory(ticket=ticket, user=project_manager)

    ghl_client.set_user(project_manager)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'input': {
                'id': str(ticket.id),
                'issues': [],
            }
        }
    )

    assert 'errors' not in response
    assert not response['data']['updateTicket']['errors']

    issue.refresh_from_db()
    assert not issue.ticket


def test_both_params_attach_and_issues(project_manager, ghl_client, ticket):
    issue = IssueFactory(user=project_manager)

    ghl_client.set_user(project_manager)

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_TICKET,
        variables={
            'input': {
                'id': str(ticket.id),
                'issues': [str(issue.id)],
                'attachIssues': [str(issue.id)],
            }
        }
    )

    assert 'errors' in response['data']['updateTicket']
    errors = response['data']['updateTicket']['errors']
    assert errors[0]['field'] == 'non_field_errors'
