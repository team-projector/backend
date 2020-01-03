from apps.development.graphql.resolvers import resolve_merge_requests_summary
from apps.development.models import MergeRequest, TeamMember
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.development.services.merge_request.summary import (
    get_merge_requests_summary,
)
from tests.helpers.objects import AttrDict
from tests.test_development.factories import (
    MergeRequestFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory


def test_counts_by_state(user):
    MergeRequestFactory.create_batch(
        7, user=user,
        state=MERGE_REQUESTS_STATES.OPENED,
        total_time_spent=0
    )
    MergeRequestFactory.create_batch(
        5, user=user,
        state=MERGE_REQUESTS_STATES.CLOSED,
        total_time_spent=0
    )
    MergeRequestFactory.create_batch(
        3, user=user,
        state=MERGE_REQUESTS_STATES.MERGED,
        total_time_spent=0
    )

    MergeRequestFactory.create_batch(
        2, user=user,
        state="",
        total_time_spent=0
    )
    MergeRequestFactory.create_batch(
        2, user=UserFactory.create(),
        state=MERGE_REQUESTS_STATES.OPENED,
        total_time_spent=0
    )

    summary = get_merge_requests_summary(
        MergeRequest.objects.filter(user=user)
    )

    assert summary.count == 17
    assert summary.opened_count == 7
    assert summary.closed_count == 5
    assert summary.merged_count == 3


def test_resolver_summary(user, client):
    team = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.LEADER)

    MergeRequestFactory.create_batch(
        7, user=user,
        state=MERGE_REQUESTS_STATES.OPENED,
        total_time_spent=0
    )

    MergeRequestFactory.create_batch(
        3, user=UserFactory(),
        state=MERGE_REQUESTS_STATES.CLOSED,
        total_time_spent=0
    )

    client.user = user
    info = AttrDict({"context": client})

    summary = resolve_merge_requests_summary(
        parent=None,
        info=info,
        user=user
    )

    assert summary.count == 7
    assert summary.opened_count == 7
    assert summary.closed_count == 0
    assert summary.merged_count == 0
