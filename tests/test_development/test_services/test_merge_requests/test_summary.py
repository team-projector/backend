# -*- coding: utf-8 -*-

from apps.development.models import MergeRequest
from apps.development.models.merge_request import MergeRequestState
from apps.development.services.merge_request.summary import (
    get_merge_requests_summary,
)
from tests.test_development.factories import MergeRequestFactory
from tests.test_users.factories.user import UserFactory


def test_counts_by_state(user):
    MergeRequestFactory.create_batch(
        7, user=user, state=MergeRequestState.OPENED, total_time_spent=0,
    )
    MergeRequestFactory.create_batch(
        5, user=user, state=MergeRequestState.CLOSED, total_time_spent=0,
    )
    MergeRequestFactory.create_batch(
        3, user=user, state=MergeRequestState.MERGED, total_time_spent=0,
    )
    MergeRequestFactory.create_batch(
        2, user=user, state="", total_time_spent=0,
    )
    MergeRequestFactory.create_batch(
        2,
        user=UserFactory.create(),
        state=MergeRequestState.OPENED,
        total_time_spent=0,
    )

    summary = get_merge_requests_summary(
        MergeRequest.objects.filter(user=user),
    )

    assert summary.count == 17
    assert summary.opened_count == 7
    assert summary.closed_count == 5
    assert summary.merged_count == 3
