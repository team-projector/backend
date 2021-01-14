from datetime import date, timedelta

import pytest

from apps.development.models.note import NoteType
from apps.payroll.services.spent_time.updater import adjust_spent_times
from tests.test_development.factories import IssueFactory, IssueNoteFactory

_SPENT = 1000


@pytest.fixture()
def issue(user):
    """Create issue for user."""
    return IssueFactory.create(user=user)


def test_filter_from_row_query(issue, gql_client_authenticated, gql_raw):
    """Test filter from raw query."""
    assert not issue.time_spents.exists()

    date_for_filter = _prepare_test_data(issue)

    assert issue.time_spents.count() == 3

    response = gql_client_authenticated.execute(
        gql_raw("all_spent_times"),
        variable_values={"date": date_for_filter},
    )

    assert "errors" not in response
    assert response["data"]["allSpentTimes"]["count"] == 1
    edges = response["data"]["allSpentTimes"]["edges"]
    assert edges[0]["node"]["timeSpent"] == float(_SPENT)


def test_filter_by_date(issue, ghl_auth_mock_info, all_spent_times_query):
    """Test filter by date."""
    assert not issue.time_spents.exists()

    date_for_filter = _prepare_test_data(issue)

    assert issue.time_spents.count() == 3

    response = all_spent_times_query(
        root=None,
        info=ghl_auth_mock_info,
        date=date_for_filter,
    )

    _check_response(response)


def _check_response(response) -> None:
    """Check response spent times."""
    assert response.length == 1
    assert response.iterable.first().time_spent == _SPENT


def _prepare_test_data(issue) -> date:
    """Prepare data for test filtering."""
    date_in_past = (issue.created_at - timedelta(days=2)).date()
    _create_spents(issue, size=2)
    _create_spents(issue, size=1, spent=_SPENT, spent_date=date_in_past)
    return date_in_past


def _create_spents(issue, size=3, spent=10, spent_date=None):
    """Create spents for issue."""
    spent_date = spent_date or issue.created_at.date()
    IssueNoteFactory.create_batch(
        size,
        content_object=issue,
        type=NoteType.TIME_SPEND,
        data={"spent": spent, "date": spent_date},
        user=issue.user,
    )
    adjust_spent_times(issue)
