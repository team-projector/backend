# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models.note import NoteType
from tests.test_development.factories import IssueFactory, IssueNoteFactory
from tests.test_payroll.factories import SalaryFactory

GHL_QUERY_ALL_SPENT_TIMES = """
query {
  allSpentTimes {
    count
    edges {
      node {
        id
      }
    }
  }
}
"""


def test_query(user, gql_client_authenticated):
    """Test getting all time spents raw query."""
    issue = IssueFactory.create(user=user)
    _create_spents(issue, 5)

    response = gql_client_authenticated.execute(GHL_QUERY_ALL_SPENT_TIMES)

    assert "errors" not in response
    assert response["data"]["allSpentTimes"]["count"] == 5


def test_not_time_spents(ghl_auth_mock_info, all_spent_times_query):
    """Test getting all time spents if not exists."""
    IssueFactory()
    response = all_spent_times_query(root=None, info=ghl_auth_mock_info)

    assert not response.length


def test_unauth(ghl_mock_info, all_spent_times_query):
    """Test unauth issues list."""
    with pytest.raises(GraphQLPermissionDenied):
        all_spent_times_query(
            root=None, info=ghl_mock_info,
        )


def test_empty_filter_by_salary(
    user, ghl_auth_mock_info, all_spent_times_query
):
    """Test filtering time spents by salary not exists."""
    issue = IssueFactory.create(user=user)
    _create_spents(issue, 5)
    salary = SalaryFactory.create(user=user)

    response = all_spent_times_query(
        root=None, info=ghl_auth_mock_info, salary=salary.id,
    )

    assert not response.length


def test_filter_by_salary(user, ghl_auth_mock_info, all_spent_times_query):
    """Test filtering time spents by salary."""
    issue = IssueFactory.create(user=user)
    _create_spents(issue, 5)

    salaries = SalaryFactory.create_batch(3, user=user)
    salary = salaries[0]

    spent_time = issue.time_spents.first()
    spent_time.salary = salary
    spent_time.save()

    response = all_spent_times_query(
        root=None, info=ghl_auth_mock_info, salary=salary.id,
    )

    assert response.length == 1
    assert response.edges[0].node.id == spent_time.id


def _create_spents(issue, size=3):
    IssueNoteFactory.create_batch(
        size,
        content_object=issue,
        type=NoteType.TIME_SPEND,
        data={"spent": 10, "date": issue.created_at.date()},
        user=issue.user,
    )
    issue.adjust_spent_times()
