from tests.test_users.factories.user import UserFactory


def test_generic(db):
    """Test basic str."""
    user = UserFactory.create(login="login_test")

    assert str(user) == "login_test"
