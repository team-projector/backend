from apps.development.models import TeamMember
from apps.development.graphql.types.merge_request import MergeRequestType
from apps.development.models import MergeRequest
from apps.development.graphql.filters import MergeRequestFilterSet
from tests.test_development.factories import (
    MergeRequestFactory, ProjectFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_all_merge_requests(user, client):
    MergeRequestFactory.create_batch(5, user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(
        MergeRequest.objects.all(), info
    )

    assert merge_requests.count() == 5


def test_filter_by_user(user, client):
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.developer
    )

    MergeRequestFactory.create(user=user_2)
    MergeRequestFactory.create_batch(3, user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'user': user_2.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first().user == user_2

    results = MergeRequestFilterSet(
        data={'user': user.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 3


def test_filter_by_state(user, client):
    merge_request_opened = MergeRequestFactory.create(
        user=user, state=MergeRequest.STATE.opened
    )
    merge_request_closed = MergeRequestFactory.create(
        user=user, state=MergeRequest.STATE.closed
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'state': MergeRequest.STATE.closed},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first() == merge_request_closed

    results = MergeRequestFilterSet(
        data={'state': MergeRequest.STATE.opened},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first() == merge_request_opened


def test_filter_by_projects(user, client):
    project_1 = ProjectFactory.create()
    MergeRequestFactory.create(user=user, project=project_1)

    project_2 = ProjectFactory.create()
    MergeRequestFactory.create(user=user, project=project_2)

    MergeRequestFactory.create_batch(
        3, user=user, project=ProjectFactory.create()
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'project': project_1.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first().project == project_1

    results = MergeRequestFilterSet(
        data={'project': project_2.id},
        queryset=merge_requests,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first().project == project_2


def test_ordering(user, client):
    merge_request_1 = MergeRequestFactory.create(title='agent', user=user)
    merge_request_2 = MergeRequestFactory.create(title='cloud', user=user)
    merge_request_3 = MergeRequestFactory.create(title='bar', user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(MergeRequest.objects.all(), info)

    results = MergeRequestFilterSet(
        data={'order_by': 'title'},
        queryset=merge_requests,
        request=client
    ).qs

    assert list(results) == [merge_request_1, merge_request_3, merge_request_2]

    results = MergeRequestFilterSet(
        data={'order_by': '-title'},
        queryset=merge_requests,
        request=client
    ).qs

    assert list(results) == [merge_request_2, merge_request_3, merge_request_1]
