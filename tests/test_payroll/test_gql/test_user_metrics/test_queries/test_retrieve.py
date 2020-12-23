def test_query(user, gql_client, ghl_raw):
    """
    Test query.

    :param user:
    :param gql_client:
    """
    gql_client.set_user(user)

    response = gql_client.execute(ghl_raw("me"))

    assert "errors" not in response
