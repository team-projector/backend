# -*- coding: utf-8 -*-

from tests.test_development.factories import MergeRequestFactory
from tests.test_development.factories.gitlab import GlMergeRequestFactory


def init_merge_request(project, gl_project, gl_kwargs=None, model_kwargs=None):
    """
    Init merge request.

    :param project:
    :param gl_project:
    :param gl_kwargs:
    :param model_kwargs:
    """
    gl_kwargs = gl_kwargs or {}
    model_kwargs = model_kwargs or {}

    gl_merge_request = GlMergeRequestFactory.create(
        project_id=gl_project["id"],
        **gl_kwargs,
    )

    merge_request = MergeRequestFactory.create(
        gl_id=gl_merge_request["id"],
        gl_iid=gl_merge_request["iid"],
        project=project,
        milestone=None,
        **model_kwargs,
    )

    return merge_request, gl_merge_request
