from apps.users.models import Token
from apps.users.graphql.mutations.login import LoginMutation
from tests.base import USER_PASSWORD
from tests.test_development.factories_gitlab import AttrDict


def test_login(user, client):
    client.user = user

    info = AttrDict({'context': client})

    assert Token.objects.filter(user=user).exists() is False

    token = LoginMutation().do_mutate(None, info, user.login, USER_PASSWORD)

    assert token is not None
    assert Token.objects.filter(user=user).exists() is True
