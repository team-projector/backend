from apps.users.services.token import create_user_token
from tests.test_users.factories.user import UserFactory


def test_generic(db):
    """Test basic str."""
    user = UserFactory.create(login='login_test')
    token = create_user_token(user)

    assert str(token) == token.key
