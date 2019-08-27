from apps.core.utils.time import seconds
from apps.development.models import TeamMember
from apps.development.graphql.types.merge_request import MergeRequestType
from apps.development.models import MergeRequest
from tests.test_development.factories import (
    MergeRequestFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_merge_requests(user, client):
    MergeRequestFactory.create_batch(2, user=user)

    user_2 = UserFactory.create()
    MergeRequestFactory.create_batch(3, user=user_2)

    team = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.leader)
    TeamMemberFactory.create(user=user_2, team=team,
                             roles=TeamMember.roles.developer)

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


def test_merge_requests_not_teamlead(user, client):
    MergeRequestFactory.create_batch(2, user=user)

    user_2 = UserFactory.create()
    MergeRequestFactory.create_batch(3, user=user_2)

    team = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.developer)
    TeamMemberFactory.create(user=user_2, team=team,
                             roles=TeamMember.roles.developer)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    merge_requests = MergeRequestType().get_queryset(
        MergeRequest.objects.all(), info
    )

    assert merge_requests.count() == 2
    assert all(item.user == user for item in merge_requests) is True


def test_metrics(user):
    merge_request = MergeRequestFactory.create(
        user=user,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )

    metrics = MergeRequestType.resolve_metrics(merge_request, None)
    assert metrics.remains == seconds(hours=1)
