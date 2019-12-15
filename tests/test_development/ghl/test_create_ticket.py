# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from apps.development.models.ticket import TYPE_FEATURE
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)

GHL_QUERY_CREATE_TICKET = """
mutation (
    $milestone: String!, $type: String!, $title: String!,
    $startDate: Date, $dueDate: Date, $url: String, $issues: [String!]
) {
createTicket(
    milestone: $milestone, type: $type, title: $title, startDate: $startDate,
    dueDate: $dueDate, url: $url, issues: $issues
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


@pytest.fixture()
def project_manager(user):
    user.roles.PROJECT_MANAGER = True
    user.save()
    yield user


@pytest.fixture()
def ticket():
    return TicketFactory(milestone=ProjectMilestoneFactory())


def test_success(project_manager, ghl_client, ticket):
    ghl_client.set_user(project_manager)
    milestone = ProjectMilestoneFactory()

    iss_1, iss_2 = IssueFactory.create_batch(size=2, user=project_manager)

    response = ghl_client.execute(
        GHL_QUERY_CREATE_TICKET,
        variables={
            'title': 'test ticket',
            'type': TYPE_FEATURE,
            'startDate': str(datetime.now().date()),
            'dueDate': str(datetime.now().date()),
            'url': 'http://test1.com',
            'milestone': str(milestone.id),
            'issues': [str(iss_1.id), str(iss_2.id)]
        }
    )

    assert 'errors' not in response
    assert not response['data']['createTicket']['errors']

    dto = response['data']['createTicket']['ticket']
    assert dto['title'] == 'test ticket'

    iss_1.refresh_from_db()
    iss_2.refresh_from_db()

    assert iss_1.ticket_id == int(dto['id'])
    assert iss_2.ticket_id == int(dto['id'])


def test_ticket_create_invalid(project_manager, ghl_client, ticket):
    ghl_client.set_user(project_manager)
    ProjectMilestoneFactory()

    response = ghl_client.execute(
        GHL_QUERY_CREATE_TICKET,
        variables={
            'title': 'test ticket',
            'type': 'invalid type',
            'url': 'invalid url',
            'milestone': ''
        }
    )
    fields_with_errors = {
        f['field']
        for f
        in response['data']['createTicket']['errors']
    }

    assert fields_with_errors == {'url', 'type', 'milestone'}


def test_without_permissions(user, ghl_client, ticket):
    ghl_client.set_user(user)
    milestone = ProjectMilestoneFactory()

    response = ghl_client.execute(
        GHL_QUERY_CREATE_TICKET,
        variables={
            'input': {
                'title': 'test ticket',
                'type': TYPE_FEATURE,
                'startDate': str(datetime.now().date()),
                'dueDate': str(datetime.now().date()),
                'url': 'http://test1.com',
                'milestone': str(milestone.id),
            }
        }
    )

    assert 'errors' in response
