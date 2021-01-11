def test_query(gql_client_authenticated, project_manager, gql_raw):
    """Test getting user raw query."""
    response = gql_client_authenticated.execute(
        gql_raw("user"),
        variable_values={"id": project_manager.id},
    )

    assert "errors" not in response
    assert response["data"]["user"]["id"] == str(project_manager.id)


def test_success(project_manager, ghl_auth_mock_info, user_query):
    """Test success user retrieving."""
    response = user_query(
        root=None,
        info=ghl_auth_mock_info,
        id=project_manager.id,
    )

    assert response == project_manager


def test_inactive(user, ghl_auth_mock_info, user_query):
    """Test success inactive user retrieving."""
    user.is_active = False
    user.save(update_fields=["is_active"])

    response = user_query(
        root=None,
        info=ghl_auth_mock_info,
        id=user.id,
    )

    assert response is None
