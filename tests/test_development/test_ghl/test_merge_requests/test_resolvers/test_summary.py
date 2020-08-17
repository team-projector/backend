# -*- coding: utf-8 -*-

from apps.development.graphql.resolvers import resolve_merge_requests_summary
from apps.development.models.merge_request import MergeRequestState
from tests.test_development.factories import MergeRequestFactory
from tests.test_users.factories.user import UserFactory


def test_resolver_summary(user, team, make_team_leader, ghl_auth_mock_info):
    """
    Test resolver summary.

    :param user:
    :param team:
    :param make_team_leader:
    :param ghl_auth_mock_info:
    """
    make_team_leader(team, user)

    MergeRequestFactory.create_batch(
        7, user=user, state=MergeRequestState.OPENED, total_time_spent=0,
    )

    MergeRequestFactory.create_batch(
        3,
        user=UserFactory(),
        state=MergeRequestState.CLOSED,
        total_time_spent=0,
    )

    summary = resolve_merge_requests_summary(
        parent=None, info=ghl_auth_mock_info, user=user,
    )

    assert summary.count == 7
    assert summary.opened_count == 7
    assert summary.closed_count == 0
    assert summary.merged_count == 0
