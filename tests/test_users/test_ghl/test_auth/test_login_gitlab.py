from django.test import override_settings

from apps.users.graphql.mutations.gitlab.login import LoginGitlabMutation
from tests.test_development.factories_gitlab import AttrDict


@override_settings(
    SOCIAL_AUTH_GITLAB_KEY='TEST_KEY',
    SOCIAL_AUTH_GITLAB_REDIRECT_URI='TEST_URI',
)
def test_login(user, client):
    client.user = user
    client.session = {}
    client.GET = {}
    client.POST = {}
    client.build_absolute_uri = _build_absolute_uri
    client.method = ''

    info = AttrDict({'context': client})

    redirect_url = LoginGitlabMutation().mutate(None, info).redirect_url

    assert 'gitlab.com/oauth/authorize' in redirect_url
    assert 'client_id=TEST_KEY' in redirect_url
    assert 'redirect_uri=TEST_URI' in redirect_url


def _build_absolute_uri(location=None):
    """Mock build."""
