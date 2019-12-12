from apps.development.models import TeamMember
from apps.development.graphql.types.merge_request import MergeRequestType
from apps.development.models import MergeRequest
from apps.development.graphql.filters import MergeRequestFilterSet
from tests.test_development.factories import (
    MergeRequestFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories.user import UserFactory


def test_merge_requests_filter_by_team_empty(user, client):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user_2])
    team_2.members.add(user_2)

    MergeRequestFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'team': team_1.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 0


def test_merge_requests_filter_by_team_watcher_empty(user, client):
    user_1 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user])
    team_2.members.add(user)

    TeamMember.objects.filter(
        team=team_1
    ).update(
        roles=TeamMember.roles.WATCHER
    )

    MergeRequestFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'team': team_1.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 0


def test_merge_requests_filter_by_team_leader(user, client):
    user_1 = UserFactory.create()

    team_1 = TeamFactory.create()

    team_1.members.set([user_1, user])

    TeamMember.objects.filter(
        user=user_1, team=team_1
    ).update(
        roles=TeamMember.roles.LEADER
    )
    TeamMember.objects.filter(
        user=user, team=team_1
    ).update(
        roles=TeamMember.roles.WATCHER
    )

    merge_request_1 = MergeRequestFactory.create(user=user_1)
    MergeRequestFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results_filtered = MergeRequestFilterSet(
        data={'team': team_1.id},
        queryset=merge_requests,
        request=client
    ).qs

    results_ids = [x.id for x in [merge_request_1]]
    results_ids.sort()

    response_ids = [x.id for x in results_filtered]
    response_ids.sort()

    assert results_ids == response_ids


def test_one_member(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    MergeRequestFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    MergeRequestFactory.create_batch(3, user=another_user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'team': team.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 2


def test_many_members(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    MergeRequestFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    MergeRequestFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'team': team.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 5


def test_many_teams(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    another_user = UserFactory.create()

    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(3, user=another_user)

    another_team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=another_team,
        roles=TeamMember.roles.WATCHER
    )

    TeamMemberFactory.create(
        user=another_user,
        team=another_team,
        roles=TeamMember.roles.DEVELOPER
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'team': team.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 2
