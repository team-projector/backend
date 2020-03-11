from apps.development.models import TeamMember
from tests.test_development.factories import (
    MergeRequestFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory


def test_merge_requests_filter_by_team_empty(
    user, ghl_auth_mock_info, all_merge_requests_query,
):
    """Test team doesn"t have merge requests."""
    user_1 = UserFactory()
    user_2 = UserFactory()

    team_1 = TeamFactory()
    team_2 = TeamFactory()

    team_1.members.set([user_1, user_2])
    team_2.members.add(user_2)

    MergeRequestFactory.create(user=user)

    response = all_merge_requests_query(
        root=None, info=ghl_auth_mock_info, team=team_1.id
    )

    assert response.length == 0


def test_merge_requests_filter_by_team_watcher_empty(
    user, ghl_auth_mock_info, all_merge_requests_query,
):
    """Test watcher no results."""
    user_1 = UserFactory()

    team_1 = TeamFactory()
    team_2 = TeamFactory()

    team_1.members.set([user_1, user])
    team_2.members.add(user)

    TeamMember.objects.filter(team=team_1).update(
        roles=TeamMember.roles.WATCHER
    )

    MergeRequestFactory.create(user=user)

    response = all_merge_requests_query(
        root=None, info=ghl_auth_mock_info, team=team_1.id
    )

    assert response.length == 0


def test_merge_requests_filter_by_team_leader(
    user, ghl_auth_mock_info, all_merge_requests_query,
):
    """Test team leader see merge requests of his team."""
    user_1 = UserFactory()
    team_1 = TeamFactory()
    team_1.members.set([user_1, user])

    TeamMember.objects.filter(user=user_1, team=team_1).update(
        roles=TeamMember.roles.LEADER
    )
    TeamMember.objects.filter(user=user, team=team_1).update(
        roles=TeamMember.roles.WATCHER
    )

    merge_request_1 = MergeRequestFactory.create(user=user_1)
    MergeRequestFactory.create(user=user)

    response = all_merge_requests_query(
        root=None, info=ghl_auth_mock_info, team=team_1.id
    )

    response_ids = [edge.node.id for edge in response.edges]
    assert response_ids == [merge_request_1.id]


def test_many_members(
    user, ghl_auth_mock_info, all_merge_requests_query,
):
    """Test team leader sees mr from multiple users in his team."""
    team = TeamFactory()

    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.LEADER
    )

    MergeRequestFactory.create_batch(2, user=user)

    another_user = UserFactory()
    MergeRequestFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user, team=team, roles=TeamMember.roles.DEVELOPER
    )
    response = all_merge_requests_query(
        root=None, info=ghl_auth_mock_info, team=team.id
    )

    assert response.length == 5


def test_many_teams(
    user, ghl_auth_mock_info, all_merge_requests_query,
):
    team = TeamFactory()

    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.LEADER
    )

    another_user = UserFactory()

    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(3, user=another_user)

    another_team = TeamFactory()
    TeamMemberFactory.create(
        user=user, team=another_team, roles=TeamMember.roles.WATCHER
    )

    TeamMemberFactory.create(
        user=another_user, team=another_team, roles=TeamMember.roles.DEVELOPER
    )

    response = all_merge_requests_query(
        root=None, info=ghl_auth_mock_info, team=team.id
    )

    assert response.length == 2
