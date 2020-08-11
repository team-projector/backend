# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils import timezone

from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import WorkBreakFactory

GHL_QUERY_TEAM_WORK_BREAKS = """
query ($team: ID, $user: ID, $offset: Int, $first: Int) {
  teamWorkBreaks(team: $team, user: $user, offset: $offset, first: $first) {
    count
    edges {
      node {
        id
        name
        workBreaks {
          edges {
            node {
              id
              fromDate
            }
          }
        }
      }
    }
  }
}
"""


def test_query(user, ghl_client):
    """Test retrieve team raw query."""
    TeamFactory.create(members=[user])

    ghl_client.set_user(user)

    response = ghl_client.execute(GHL_QUERY_TEAM_WORK_BREAKS)

    assert "errors" not in response
    assert response["data"]["teamWorkBreaks"]["count"] == 1


def test_query_with_dates(user, ghl_client):
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

    ghl_client.set_user(user)

    response = ghl_client.execute(GHL_QUERY_TEAM_WORK_BREAKS)

    assert "errors" not in response

    response_work_breaks = response["data"]["teamWorkBreaks"]
    assert response_work_breaks["count"] == 1

    _check_work_breaks(response_work_breaks["edges"][0]["node"], work_breaks)


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

    assert response.length == 1
    node = response.edges[0].node
    assert not node.work_breaks.exists()


def _check_work_breaks(response, work_breaks):
    """Checking work breaks in response."""
    edges = response["workBreaks"]["edges"]

    assert len(edges) == len(work_breaks)
    _assert_id(edges[0], work_breaks[1])
    _assert_id(edges[1], work_breaks[0])
    _assert_id(edges[2], work_breaks[2])


def _assert_id(source, current_obj):
    assert source["node"]["id"] == str(current_obj.id)