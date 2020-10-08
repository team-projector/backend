import re

import httpretty
import pytest
from constance import config
from graphene_django.rest_framework.tests.test_mutation import mock_info
from graphql import ResolveInfo
from social_core.backends.gitlab import GitLabOAuth2

from apps.core.gitlab.client import get_default_gitlab_client
from tests.helpers.httpretty_mock import HttprettyMock, RequestCallbackFactory

RE_GITLAB_URL = re.compile(r"https://gitlab\.com.*")


class GitlabMock(HttprettyMock):
    """Gitlab mock."""

    base_api_url = "{0}/api/v4".format(config.GITLAB_ADDRESS)

    def __init__(self) -> None:
        """Initializing."""
        super().__init__()

        self.register_url(
            httpretty.GET,
            RE_GITLAB_URL,
            RequestCallbackFactory({}),
        )
        self.register_url(
            httpretty.POST,
            RE_GITLAB_URL,
            RequestCallbackFactory({}),
        )
        self.register_url(
            httpretty.DELETE,
            RE_GITLAB_URL,
            RequestCallbackFactory({}),
        )


@pytest.fixture()
def gl_mocker():
    """Gl mocker."""
    httpretty.enable(allow_net_connect=False)

    yield GitlabMock()

    httpretty.disable()


@pytest.fixture()
def gl_client(gl_mocker):
    """
    Gl client.

    :param gl_mocker:
    """
    return get_default_gitlab_client()


@pytest.fixture()
def gl_token_request_info(rf) -> ResolveInfo:
    """
    Gl token request info.

    :param rf:
    :rtype: ResolveInfo
    """
    request = rf.get(GitLabOAuth2.AUTHORIZATION_URL)
    setattr(request, "session", {"gitlab_state": "gitlab_state"})  # noqa: B010

    resolve_info = mock_info()
    resolve_info.context = request

    return resolve_info
