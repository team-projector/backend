from tests.test_development.factories import IssueFactory


def test_success_query(user, gql_client, gql_raw):
    """Test user metrics raw query."""
    gql_client.set_user(user)
    user.roles.MANAGER = True
    user.save()

    IssueFactory.create(user=user)

    response = gql_client.execute(
        gql_raw("user_metrics"),
        variable_values={
            "id": user.pk,
        },
    )

    assert "errors" not in response

    metrics = response["data"]["user"]["metrics"]

    assert metrics["issues"]["openedCount"] == 1
