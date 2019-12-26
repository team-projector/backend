# -*- coding: utf-8 -*-

from tests.test_development.factories import ProjectFactory
from tests.test_development.factories.gitlab import GlProjectFactory


def init_project(gl_kwargs=None, model_kwargs=None):
    gl_kwargs = gl_kwargs or {}
    model_kwargs = model_kwargs or {}

    gl_project = GlProjectFactory.create(**model_kwargs)
    project = ProjectFactory.create(gl_id=gl_project['id'], **gl_kwargs)

    return project, gl_project
