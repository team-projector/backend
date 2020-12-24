import pytest
from constance import config
from django.conf import settings
from social_core.backends.gitlab import GitLabOAuth2


@pytest.fixture(autouse=True)
def _gitlab_login(override_config) -> None:
    """Forces django to use gitlab settings."""
    settings.SOCIAL_AUTH_GITLAB_REDIRECT_URI = "redirect_uri"
    with override_config(
        OAUTH_GITLAB_KEY="test_gitlab_key",
        OAUTH_GITLAB_SECRET="test_gitlab_secret",
    ):
        yield


def test_query(user, gql_client, gql_raw):
    """Test raw query."""
    context = {
        "session": {},
        "GET": {},
        "POST": {},
        "build_absolute_uri": lambda mock: mock,
        "method": "",
    }

    response = gql_client.execute(
        gql_raw("login_gitlab"),
        extra_context=context,
    )

    redirect_url = response["data"]["loginGitlab"]["redirectUrl"]

    client = "client_id={0}".format(config.OAUTH_GITLAB_KEY)
    redirect = "redirect_uri={0}".format(
        settings.SOCIAL_AUTH_GITLAB_REDIRECT_URI,
    )

    assert redirect_url.startswith(GitLabOAuth2.AUTHORIZATION_URL)
    assert client in redirect_url
    assert redirect in redirect_url
