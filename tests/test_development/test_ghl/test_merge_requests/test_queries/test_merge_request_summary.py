from tests.test_development.factories import MergeRequestFactory


def test_query(user, ghl_client, ghl_raw):
    """Test getting merge requests summary via a raw query."""
    MergeRequestFactory(user=user)

    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw("merge_requests_summary"),
        variable_values={"user": user.id},
    )

    assert "errors" not in response
    assert response["data"]["mergeRequestsSummary"]["count"] == 1
    assert response["data"]["mergeRequestsSummary"]["openedCount"] == 1
    assert response["data"]["mergeRequestsSummary"]["closedCount"] == 0
    assert response["data"]["mergeRequestsSummary"]["mergedCount"] == 0
