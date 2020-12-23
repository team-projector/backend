from tests.test_users.factories.user import UserFactory


def test_generic(token_service, db):
    """Test basic str."""
    user = UserFactory.create(login="login_test")
    token = token_service.create_user_token(user)

    assert str(token) == token.key
