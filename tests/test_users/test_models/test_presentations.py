from apps.users.services.token import create_user_token
from tests.test_users.factories.user import UserFactory


def test_token(db):
  user = UserFactory.create(login='login_test')
  token = create_user_token(user)

  assert str(token) == token.key


def test_user(db):
  user = UserFactory.create(login='login_test')

  assert str(user) == 'login_test'
