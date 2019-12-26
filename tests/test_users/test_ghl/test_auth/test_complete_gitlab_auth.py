# -*- coding: utf-8 -*-

from apps.users.graphql.mutations.auth import CompleteGitlabAuthMutation
from apps.users.models import Token
from tests.helpers.httpretty_mock import RequestCallbackFactory
from tests.helpers.objects import AttrDict


def test_complete_auth(user, client, gl_mocker):
    gl_mocker.register_get('/user', {'username': user.login})

    gl_mocker.register_url(
        method='POST',
        uri='https://gitlab.com/oauth/token',
        request_callback=RequestCallbackFactory({
            'access_token': 'TEST_TOKEN',
        }),
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
    gl_mocker.register_get('/user', {'username': 'test user'})

    gl_mocker.register_url(
        method='POST',
        uri='https://gitlab.com/oauth/token',
        request_callback=RequestCallbackFactory({
            'access_token': 'TEST_TOKEN',
        }),
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
