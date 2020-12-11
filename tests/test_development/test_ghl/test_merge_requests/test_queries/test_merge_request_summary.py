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

    merge_requests_summary = response["data"]["mergeRequestsSummary"]

    assert merge_requests_summary["count"] == 1
    assert merge_requests_summary["openedCount"] == 1
    assert not merge_requests_summary["closedCount"]
    assert not merge_requests_summary["mergedCount"]
