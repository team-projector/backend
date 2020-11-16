def test_query(user, ghl_client, ghl_raw):
    """
    Test query.

    :param user:
    :param ghl_client:
    """
    ghl_client.set_user(user)

    response = ghl_client.execute(ghl_raw("me"))

    assert "errors" not in response
