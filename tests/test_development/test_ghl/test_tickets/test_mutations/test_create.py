# -*- coding: utf-8 -*-

from datetime import datetime

import pytest
from pytest import raises

from apps.core.graphql.errors import (
    INPUT_ERROR,
    GraphQLInputError,
    GraphQLPermissionDenied,
)
from apps.development.models.ticket import TYPE_FEATURE
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)

GHL_QUERY_CREATE_TICKET = """
mutation (
    $milestone: ID!, $type: String!, $title: String!, $role: String,
    $startDate: Date, $dueDate: Date, $url: String, $issues: [ID!]
) {
createTicket(
    milestone: $milestone, type: $type, title: $title, startDate: $startDate,
    dueDate: $dueDate, url: $url, issues: $issues, role: $role
) {
    ticket {
      id
      title
      }
    }
  }
"""


@pytest.fixture()
def ticket():
    return TicketFactory(milestone=ProjectMilestoneFactory())


def test_query(project_manager, ghl_client):
    """Test create ticket raw query."""
    ghl_client.set_user(project_manager)

    milestone = ProjectMilestoneFactory()

    issues = IssueFactory.create_batch(size=2, user=project_manager)

    response = ghl_client.execute(
        GHL_QUERY_CREATE_TICKET,
        variables={
            "title": "test ticket",
            "type": TYPE_FEATURE,
            "startDate": str(datetime.now().date()),
            "dueDate": str(datetime.now().date()),
            "url": "http://test1.com",
            "milestone": str(milestone.id),
            "issues": [str(issue.pk) for issue in issues],
            "role": "Manager"
        }
    )

    assert "errors" not in response

    dto = response["data"]["createTicket"]["ticket"]
    assert dto["title"] == "test ticket"

    for issue in issues:
        issue.refresh_from_db()
        assert issue.ticket_id == int(dto["id"])


def test_invalid_parameters(
    project_manager,
    ghl_auth_mock_info,
    create_ticket_mutation,
):
    """Test creation with invalid parameters."""
    with raises(GraphQLInputError) as exc_info:
        create_ticket_mutation(
            root=None,
            info=ghl_auth_mock_info,
            title="test ticket",
            type="invalid type",
            url="invalid url",
            milestone=""
        )

    extensions = exc_info.value.extensions  # noqa:WPS441
    assert extensions["code"] == INPUT_ERROR

    fields_with_errors = {
        err["fieldName"]
        for err in extensions["fieldErrors"]
    }

    assert fields_with_errors == {"url", "type", "milestone"}


def test_without_permissions(user, ghl_auth_mock_info, create_ticket_mutation):
    """Test deletion without permissions."""
    milestone = ProjectMilestoneFactory()

    with raises(GraphQLPermissionDenied):
        create_ticket_mutation(
            root=None,
            info=ghl_auth_mock_info,
            title="test ticket",
            startDate=datetime.now().date(),
            dueDate=datetime.now().date(),
            type=TYPE_FEATURE,
            url="http://test1.com",
            milestone=milestone.pk
        )
