from datetime import timedelta

from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models.note import NoteType
from apps.payroll.services.spent_time.updater import adjust_spent_times
from tests.test_development.factories import IssueFactory, IssueNoteFactory
from tests.test_payroll.factories import SalaryFactory


def test_query(user, gql_client_authenticated, gql_raw):
    """Test getting all time spents raw query."""
    issue = IssueFactory.create(user=user)
    _create_spents(issue, 5)

    response = gql_client_authenticated.execute(gql_raw("all_spent_times"))

    assert "errors" not in response
    assert response["data"]["allSpentTimes"]["count"] == 5


def test_not_time_spents(ghl_auth_mock_info, all_spent_times_query):
    """Test getting all time spents if not exists."""
    IssueFactory()
    response = all_spent_times_query(root=None, info=ghl_auth_mock_info)

    assert not response.length


def test_unauth(ghl_mock_info, all_spent_times_query):
    """Test unauth issues list."""
    response = all_spent_times_query(
        root=None,
        info=ghl_mock_info,
    )
    assert isinstance(response, GraphQLPermissionDenied)


def test_empty_filter_by_salary(
    user,
    ghl_auth_mock_info,
    all_spent_times_query,
):
    """Test filtering time spents by salary not exists."""
    issue = IssueFactory.create(user=user)
    _create_spents(issue, 5)
    salary = SalaryFactory.create(user=user)

    response = all_spent_times_query(
        root=None,
        info=ghl_auth_mock_info,
        salary=salary.id,
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
        root=None,
        info=ghl_auth_mock_info,
        salary=salary.id,
    )

    assert response.length == 1
    assert response.edges[0].node.id == spent_time.id


def test_filter_by_date(user, ghl_auth_mock_info, all_spent_times_query):
    """Test filter by date."""
    spent = 1000
    issue = IssueFactory.create(user=user)
    date_in_past = (issue.created_at - timedelta(days=2)).date()
    IssueNoteFactory.create(
        content_object=issue,
        type=NoteType.TIME_SPEND,
        data={"spent": spent, "date": date_in_past},
        user=issue.user,
    )
    _create_spents(issue, 1)
    assert issue.time_spents.count() == 2

    response = all_spent_times_query(
        root=None,
        info=ghl_auth_mock_info,
        date=date_in_past,
    )

    assert response.length == 1
    assert response.iterable.first().time_spent == spent


def _create_spents(issue, size=3):
    """
    Create spents.

    :param issue:
    :param size:
    """
    IssueNoteFactory.create_batch(
        size,
        content_object=issue,
        type=NoteType.TIME_SPEND,
        data={"spent": 10, "date": issue.created_at.date()},
        user=issue.user,
    )
    adjust_spent_times(issue)
