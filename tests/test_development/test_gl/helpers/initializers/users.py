# -*- coding: utf-8 -*-

from tests.test_development.test_gl.helpers import gl_mock
from tests.test_users.factories.gitlab import GlUserFactory


def init_user(mocker, gl_kwargs=None):
    gl_kwargs = gl_kwargs or {}

    gl_user = GlUserFactory.create(**gl_kwargs)
    gl_mock.register_user(mocker, gl_user)

    return gl_user
