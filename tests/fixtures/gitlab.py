# -*- coding: utf-8 -*-

import httpretty
import pytest

from apps.core.gitlab.client import get_default_gitlab_client
from tests.helpers.mocks.gitlab import GitlabMock
from tests.test_development.factories_gitlab import GlUserFactory


@pytest.fixture()
def gl_mocker():
    httpretty.enable(allow_net_connect=False)

    yield GitlabMock()

    httpretty.disable()


@pytest.fixture()
def gl_client(gl_mocker):
    gl_mocker.registry_get('/user', GlUserFactory())

    return get_default_gitlab_client()
