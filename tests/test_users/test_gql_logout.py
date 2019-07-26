from apps.users.models import Token
from apps.users.services.token import create_user_token
from apps.users.graphql.mutations.logout import LogoutMutation
from tests.test_development.factories_gitlab import AttrDict


def test_logout(user, client):
    client.user = user
    client.auth = create_user_token(user)

    info = AttrDict({'context': client})

    assert Token.objects.filter(user=user).exists() is True

    LogoutMutation().mutate(None, info)

    assert Token.objects.filter(user=user).exists() is False
