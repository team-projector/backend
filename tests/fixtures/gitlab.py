# -*- coding: utf-8 -*-

import re

import httpretty
import pytest
from django.conf import settings

from apps.core.gitlab.client import get_default_gitlab_client
from tests.helpers.httpretty_mock import HttprettyMock, RequestCallbackFactory

RE_GITLAB_URL = re.compile(r'https://gitlab\.com.*')


class GitlabMock(HttprettyMock):
    base_api_url = '{0}/api/v4'.format(settings.GITLAB_HOST)

    def __init__(self) -> None:
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
    httpretty.enable(allow_net_connect=False)

    yield GitlabMock()

    httpretty.disable()


@pytest.fixture()
def gl_client(gl_mocker):
    return get_default_gitlab_client()
