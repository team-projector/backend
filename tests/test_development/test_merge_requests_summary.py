from apps.development.services.summary.merge_requests import \
    get_merge_requests_summary
from apps.development.models import MergeRequest
from tests.test_development.factories import MergeRequestFactory


def test_counts_by_state(user):
    MergeRequestFactory.create_batch(
        7, user=user,
        state=MergeRequest.STATE.opened,
        total_time_spent=0
    )
    MergeRequestFactory.create_batch(
        5, user=user,
        state=MergeRequest.STATE.closed,
        total_time_spent=0
    )
    MergeRequestFactory.create_batch(
        3, user=user,
        state=MergeRequest.STATE.merged,
        total_time_spent=0
    )
    MergeRequestFactory.create_batch(
        2, user=user,
        state=None,
        total_time_spent=0
    )

    summary = get_merge_requests_summary(
        MergeRequest.objects.filter(user=user),
        project=None,
        team=None,
        user=user
    )

    assert summary.count == 17
    assert summary.opened_count == 7
    assert summary.closed_count == 5
    assert summary.merged_count == 3
