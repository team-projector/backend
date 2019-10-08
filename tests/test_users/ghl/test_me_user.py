from apps.users.graphql.resolvers import resolve_me_user
from tests.test_development.factories_gitlab import AttrDict


def test_me_user(user, client):
    client.user = user

    info = AttrDict({'context': client})

    assert resolve_me_user(None, info) == user
