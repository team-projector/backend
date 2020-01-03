# -*- coding: utf-8 -*-

from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories.gitlab import GlGroupFactory


def init_group(gl_kwargs=None, model_kwargs=None):
    gl_kwargs = gl_kwargs or {}
    model_kwargs = model_kwargs or {}

    gl_group = GlGroupFactory.create(**gl_kwargs)
    group = ProjectGroupFactory.create(gl_id=gl_group["id"], **model_kwargs)

    return group, gl_group
