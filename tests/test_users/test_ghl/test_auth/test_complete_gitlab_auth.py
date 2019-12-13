from apps.users.graphql.mutations.gitlab.complete_gitlab_auth import (
    CompleteGitlabAuthMutation,
)
from apps.users.models import Token
from tests.test_development.factories_gitlab import AttrDict


def test_complete_auth(user, client, gl_mocker):
    gl_mocker.registry_get('/user', {'username': user.login})

    gl_mocker._registry_url(
        method='POST',
        uri='https://gitlab.com/oauth/token',
        data={'access_token': 'TEST_TOKEN'},
        priority=1
    )

    client.session = {'gitlab_state': 'test_state'}
    client.GET = {}
    client.POST = {}
    client.build_absolute_uri = _build_absolute_uri
    client.method = ''

    info = AttrDict({'context': client})

    assert Token.objects.count() == 0

    token = CompleteGitlabAuthMutation().mutate(
        root=None,
        info=info,
        code='test_code',
        state='test_state'
    ).token

    assert Token.objects.count() == 1
    assert Token.objects.first() == token


def test_user_not_existed(db, client, gl_mocker):
    gl_mocker.registry_get('/user', {'username': 'test user'})

    gl_mocker._registry_url(
        method='POST',
        uri='https://gitlab.com/oauth/token',
        data={'access_token': 'TEST_TOKEN'},
        priority=1
    )

    client.session = {'gitlab_state': 'test_state'}
    client.GET = {}
    client.POST = {}
    client.build_absolute_uri = _build_absolute_uri
    client.method = ''

    info = AttrDict({'context': client})

    assert Token.objects.count() == 0

    CompleteGitlabAuthMutation().mutate(
        root=None,
        info=info,
        code='test_code',
        state='test_state'
    )

    assert Token.objects.count() == 0


def _build_absolute_uri(location=None):
    """Mock build."""
