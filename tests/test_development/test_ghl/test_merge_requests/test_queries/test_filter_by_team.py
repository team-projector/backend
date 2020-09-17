# -*- coding: utf-8 -*-

from apps.development.models import TeamMember
from tests.test_development.factories import (
    MergeRequestFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory


def test_filter_by_team_empty(
    user,
    ghl_auth_mock_info,
    all_merge_requests_query,
):
    """Test team doesn"t have merge requests."""
    user1 = UserFactory()
    user2 = UserFactory()

    team1 = TeamFactory()
    team2 = TeamFactory()

    team1.members.set([user1, user2])
    team2.members.add(user2)

    MergeRequestFactory.create(user=user)

    response = all_merge_requests_query(
        root=None,
        info=ghl_auth_mock_info,
        team=team1.id,
    )

    assert response.length == 0


def test_filter_by_team_watcher_empty(
    user,
    ghl_auth_mock_info,
    all_merge_requests_query,
):
    """Test watcher no results."""
    user1 = UserFactory()

    team1 = TeamFactory()
    team2 = TeamFactory()

    team1.members.set([user1, user])
    team2.members.add(user)

    TeamMember.objects.filter(team=team1).update(
        roles=TeamMember.roles.WATCHER,
    )

    MergeRequestFactory.create(user=user)

    response = all_merge_requests_query(
        root=None,
        info=ghl_auth_mock_info,
        team=team1.id,
    )

    assert response.length == 0


def test_filter_by_team_leader(
    user,
    ghl_auth_mock_info,
    all_merge_requests_query,
):
    """Test team leader see merge requests of his team."""
    user1 = UserFactory()
    team1 = TeamFactory()
    team1.members.set([user1, user])

    TeamMember.objects.filter(user=user1, team=team1).update(
        roles=TeamMember.roles.LEADER,
    )
    TeamMember.objects.filter(user=user, team=team1).update(
        roles=TeamMember.roles.WATCHER,
    )

    merge_request1 = MergeRequestFactory.create(user=user1)
    MergeRequestFactory.create(user=user)

    response = all_merge_requests_query(
        root=None,
        info=ghl_auth_mock_info,
        team=team1.id,
    )

    response_ids = [edge.node.id for edge in response.edges]
    assert response_ids == [merge_request1.id]


def test_many_members(
    user,
    ghl_auth_mock_info,
    all_merge_requests_query,
):
    """Test team leader sees mr from multiple users in his team."""
    team = TeamFactory()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )

    MergeRequestFactory.create_batch(2, user=user)

    another_user = UserFactory()
    MergeRequestFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user,
        team=team,
        roles=TeamMember.roles.DEVELOPER,
    )
    response = all_merge_requests_query(
        root=None,
        info=ghl_auth_mock_info,
        team=team.id,
    )

    assert response.length == 5


def test_many_teams(
    user,
    ghl_auth_mock_info,
    all_merge_requests_query,
):
    """
    Test many teams.

    :param user:
    :param ghl_auth_mock_info:
    :param all_merge_requests_query:
    """
    team = TeamFactory()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )

    another_user = UserFactory()

    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(3, user=another_user)

    another_team = TeamFactory()
    TeamMemberFactory.create(
        user=user,
        team=another_team,
        roles=TeamMember.roles.WATCHER,
    )

    TeamMemberFactory.create(
        user=another_user,
        team=another_team,
        roles=TeamMember.roles.DEVELOPER,
    )

    response = all_merge_requests_query(
        root=None,
        info=ghl_auth_mock_info,
        team=team.id,
    )

    assert response.length == 2
