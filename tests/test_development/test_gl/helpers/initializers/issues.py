# -*- coding: utf-8 -*-

from tests.test_development.factories import IssueFactory
from tests.test_development.factories.gitlab import GlIssueFactory


def init_issue(project, gl_project, gl_kwargs=None, model_kwargs=None):
    """
    Init issue.

    :param project:
    :param gl_project:
    :param gl_kwargs:
    :param model_kwargs:
    """
    gl_kwargs = gl_kwargs or {}
    model_kwargs = model_kwargs or {}

    gl_issue = GlIssueFactory.create(project_id=gl_project["id"], **gl_kwargs)

    issue = IssueFactory.create(
        gl_id=gl_issue["id"],
        gl_iid=gl_issue["iid"],
        project=project,
        **model_kwargs,
    )

    return issue, gl_issue
