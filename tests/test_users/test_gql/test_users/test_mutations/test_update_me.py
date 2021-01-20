def test_query(user, gql_client, gql_raw):
    """Test login raw query."""
    gql_client.set_user(user)

    old_email = user.email

    response = gql_client.execute(
        gql_raw("update_me"),
        variable_values={
            "input": {
                "name": "new name",
                "glToken": "new gl token",
            },
        },
    )

    assert "errors" not in response

    user.refresh_from_db()

    assert user.name == "new name"
    assert user.gl_token == "new gl token"
    assert user.email == old_email


def test_unauth(user, gql_client, gql_raw):
    """Test success login."""
    response = gql_client.execute(
        gql_raw("update_me"),
        variable_values={
            "input": {
                "name": "new name",
                "glToken": "new gl token",
            },
        },
    )

    assert "errors" in response


def test_none(user, ghl_auth_mock_info, update_me_mutation):
    """Test reset gl token."""
    user.gl_token = "gl token"
    user.save()

    update_me_mutation(
        root=None,
        info=ghl_auth_mock_info,
        input={
            "gl_token": None,
        },
    )

    user.refresh_from_db()

    assert not user.gl_token
