# -*- coding: utf-8 -*-

from datetime import datetime

import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory

GHL_QUERY_TEAM_PROGRESS_METRICS = """
query ($id: ID!, $start: Date!, $end: Date!, $group: String!) {
  teamProgressMetrics(team: $id, start: $start, end: $end, group: $group) {
    metrics {
      start
      end
      issuesCount
    }
  }
}
"""


def test_query(user, ghl_client):
    """Test team progress metrics raw query."""
    team = TeamFactory.create()
    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.LEADER,
    )

    ghl_client.set_user(user)

    date = datetime.now().date()

    response = ghl_client.execute(
        GHL_QUERY_TEAM_PROGRESS_METRICS,
        variable_values={
            "id": team.pk,
            "start": date,
            "end": date,
            "group": "day",
        },
    )

    progress_metrics = response["data"]["teamProgressMetrics"]

    assert len(progress_metrics) == 1

    metrics = progress_metrics[0]["metrics"]

    assert len(metrics) == 1
    assert metrics[0]["start"] == date.strftime("%Y-%m-%d")  # noqa: WPS323
    assert metrics[0]["end"] == date.strftime("%Y-%m-%d")  # noqa: WPS323
    assert not metrics[0]["issuesCount"]


def test_not_leader(user, ghl_auth_mock_info, team_progress_metrics_query):
    """Test request not leader."""
    team = TeamFactory.create(members=[user])
    date = datetime.now().date()

    with pytest.raises(GraphQLPermissionDenied):
        team_progress_metrics_query(
            None,
            info=ghl_auth_mock_info,
            team=team.pk,
            start=date,
            end=date,
            group="day",
        )


def test_another_team(user, ghl_auth_mock_info, team_progress_metrics_query):
    """Test retrieve metrics for another team."""
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )
    date = datetime.now().date()

    with pytest.raises(GraphQLPermissionDenied):
        team_progress_metrics_query(
            None,
            info=ghl_auth_mock_info,
            team=TeamFactory.create().pk,
            start=date,
            end=date,
            group="day",
        )


def test_metrics_developer(
    user,
    ghl_auth_mock_info,
    team_progress_metrics_query,
):
    """Test retrieve metrics for developer."""
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER,
    )
    date = datetime.now().date()

    with pytest.raises(GraphQLPermissionDenied):
        team_progress_metrics_query(
            None,
            info=ghl_auth_mock_info,
            team=team.pk,
            start=date,
            end=date,
            group="day",
        )
