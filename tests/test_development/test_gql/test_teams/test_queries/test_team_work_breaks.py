from datetime import timedelta

from django.utils import timezone

from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import WorkBreakFactory


def test_query(user, gql_client, gql_raw):
    """Test retrieve team raw query."""
    TeamFactory.create(members=[user])
    WorkBreakFactory.create(user=user)

    gql_client.set_user(user)

    response = gql_client.execute(gql_raw("team_work_breaks"))

    assert "errors" not in response
    assert response["data"]["teamWorkBreaks"]["count"] == 1


def test_query_with_dates(user, gql_client, gql_raw):
    """
    Test query with dates.

    :param user:
    :param gql_client:
    """
    base_date = timezone.now()

    TeamFactory.create(members=[user])
    work_breaks = [
        WorkBreakFactory.create(
            user=user,
            from_date=base_date - timedelta(days=10),
            to_date=base_date + timedelta(days=1),
        ),
        WorkBreakFactory.create(
            user=user,
            from_date=base_date - timedelta(days=20),
            to_date=base_date - timedelta(days=15),
        ),
        WorkBreakFactory.create(
            user=user,
            from_date=base_date + timedelta(days=10),
            to_date=base_date + timedelta(days=21),
        ),
    ]

    gql_client.set_user(user)

    response = gql_client.execute(gql_raw("team_work_breaks"))

    assert "errors" not in response

    response_work_breaks = response["data"]["teamWorkBreaks"]
    assert response_work_breaks["count"] == 3

    _check_work_breaks(
        response_work_breaks["edges"],
        [
            work_breaks[2],
            work_breaks[0],
            work_breaks[1],
        ],
    )


def test_success(user, ghl_auth_mock_info, team_work_breaks_query):
    """Test success."""
    TeamFactory.create(members=[user])
    WorkBreakFactory.create(user=user)

    response = team_work_breaks_query(root=None, info=ghl_auth_mock_info)

    assert response.length


def test_not_work_breaks(user, ghl_auth_mock_info, team_work_breaks_query):
    """Test not work breaks."""
    TeamFactory.create(members=[user])
    WorkBreakFactory.create()

    response = team_work_breaks_query(root=None, info=ghl_auth_mock_info)

    assert not response.length


def _check_work_breaks(response, work_breaks):
    """Checking work breaks in response."""
    assert len(response) == len(work_breaks)
    for response_wb, work_break in zip(response, work_breaks):
        _assert_id(response_wb, work_break)


def _assert_id(source, current_obj):
    """
    Assert id.

    :param source:
    :param current_obj:
    """
    assert source["node"]["id"] == str(current_obj.id)
