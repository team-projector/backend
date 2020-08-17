# -*- coding: utf-8 -*-

from collections import namedtuple

import pytest

from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.factories import ProjectMilestoneFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory

Context = namedtuple(
    "Context",
    [
        "project",
        "gl_project",
        "gl_assignee",
        "gl_author",
        "merge_request",
        "gl_merge_request",
    ],
)


@pytest.fixture()
def context(gl_mocker) -> Context:
    """
    Context.

    :param gl_mocker:
    :rtype: Context
    """
    project, gl_project = initializers.init_project()
    gl_user = GlUserFactory.create()
    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"assignee": gl_user, "author": gl_user},
    )

    gl_mock.register_user(gl_mocker, gl_user)
    gl_mock.mock_merge_request_endpoints(
        gl_mocker, gl_project, gl_merge_request,
    )
    gl_mock.mock_project_endpoints(
        gl_mocker, gl_project, merge_requests=[gl_merge_request],
    )

    return Context(
        project=project,
        gl_project=gl_project,
        gl_assignee=gl_user,
        gl_author=gl_user,
        merge_request=merge_request,
        gl_merge_request=gl_merge_request,
    )


def test_load(db, context):
    """
    Test load.

    :param db:
    :param context:
    """
    MergeRequestGlManager().sync_merge_requests()

    context.merge_request.refresh_from_db()

    gl_checkers.check_merge_request(
        context.merge_request, context.gl_merge_request,
    )
    gl_checkers.check_user(context.merge_request.user, context.gl_assignee)
    gl_checkers.check_user(context.merge_request.author, context.gl_author)


def test_no_milestone_in_db(db, context, gl_client):
    """
    Test no milestone in db.

    :param db:
    :param context:
    :param gl_client:
    """
    gl_project_loaded = gl_client.projects.get(id=context.project.gl_id)

    MergeRequestGlManager().sync_project_merge_requests(
        context.project, gl_project_loaded,
    )

    merge_request = context.merge_request
    merge_request.refresh_from_db()

    gl_checkers.check_merge_request(merge_request, context.gl_merge_request)
    gl_checkers.check_user(merge_request.user, context.gl_assignee)
    assert merge_request.milestone is None


def test_milestone_in_db(db, context, gl_client):
    """
    Test milestone in db.

    :param db:
    :param context:
    :param gl_client:
    """
    milestone = ProjectMilestoneFactory.create(
        gl_id=context.gl_merge_request["milestone"]["id"],
    )

    gl_project_loaded = gl_client.projects.get(id=context.project.gl_id)

    MergeRequestGlManager().sync_project_merge_requests(
        context.project, gl_project_loaded,
    )

    merge_request = context.merge_request
    merge_request.refresh_from_db()

    gl_checkers.check_merge_request(merge_request, context.gl_merge_request)
    gl_checkers.check_user(merge_request.user, context.gl_assignee)
    assert merge_request.milestone == milestone
