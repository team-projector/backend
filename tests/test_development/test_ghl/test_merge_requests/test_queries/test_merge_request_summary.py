# -*- coding: utf-8 -*-

from tests.test_development.factories import MergeRequestFactory

GHL_QUERY_MERGE_REQUEST_SUMMARY = """
query ($user: ID!) {
  mergeRequestsSummary (user: $user) {
    count
    openedCount
    closedCount
    mergedCount
  }
}
"""


def test_query(user, ghl_client):
    """Test getting merge requests summary via a raw query."""
    MergeRequestFactory(user=user)

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_MERGE_REQUEST_SUMMARY,
        variables={
            'user': user.id,
        },
    )

    assert 'errors' not in response
    assert response['data']['mergeRequestsSummary']['count'] == 1
    assert response['data']['mergeRequestsSummary']['openedCount'] == 1
    assert response['data']['mergeRequestsSummary']['closedCount'] == 0
    assert response['data']['mergeRequestsSummary']['mergedCount'] == 0
