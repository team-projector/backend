# -*- coding: utf-8 -*-

from collections import namedtuple

import pytest
from django.utils import timezone

from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories import ProjectMilestoneFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory

Context = namedtuple(
    "Context", ["project", "gl_project", "gl_assignee", "issue", "gl_issue"],
)


@pytest.fixture()
def context(gl_mocker) -> Context:
    """
    Context.

    :param gl_mocker:
    :rtype: Context
    """
    project, gl_project = initializers.init_project()
    gl_assignee = GlUserFactory.create()
    issue, gl_issue = initializers.init_issue(
        project, gl_project, gl_kwargs={"assignee": gl_assignee},
    )

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_issue_endpoints(gl_mocker, gl_project, gl_issue)
    gl_mock.mock_project_endpoints(
        gl_mocker, gl_project, issues=[gl_issue],
    )

    return Context(
        project=project,
        gl_project=gl_project,
        gl_assignee=gl_assignee,
        issue=issue,
        gl_issue=gl_issue,
    )


def test_load(db, context):
    """
    Test load.

    :param db:
    :param context:
    """
    IssueGlManager().sync_issues()

    context.issue.refresh_from_db()

    gl_checkers.check_issue(context.issue, context.gl_issue)
    gl_checkers.check_user(context.issue.user, context.gl_assignee)


def test_update_last_sync(db, context):
    """
    Test update last sync.

    :param db:
    :param context:
    """
    IssueGlManager().sync_project_issues(context.project)

    issue = Issue.objects.first()

    gl_checkers.check_issue(issue, context.gl_issue)

    context.project.refresh_from_db()
    assert (
        timezone.datetime.date(context.project.gl_last_issues_sync)
        == timezone.now().date()
    )


def test_no_milestone_in_db(db, context, gl_client):
    """
    Test no milestone in db.

    :param db:
    :param context:
    :param gl_client:
    """
    gl_project_loaded = gl_client.projects.get(id=context.project.gl_id)
    gl_issue_manager = gl_project_loaded.issues.get(id=context.gl_issue["iid"])

    IssueGlManager().update_project_issue(
        context.project, gl_project_loaded, gl_issue_manager,
    )

    issue = Issue.objects.first()

    assert issue is not None

    gl_checkers.check_issue(issue, context.gl_issue)
    gl_checkers.check_user(issue.user, context.gl_assignee)
    assert issue.milestone is None


def test_milestone_in_db(db, context, gl_client):
    """
    Test milestone in db.

    :param db:
    :param context:
    :param gl_client:
    """
    milestone = ProjectMilestoneFactory.create(
        gl_id=context.gl_issue["milestone"]["id"],
    )

    gl_project_loaded = gl_client.projects.get(id=context.project.gl_id)
    gl_issue_manager = gl_project_loaded.issues.get(id=context.gl_issue["iid"])

    IssueGlManager().update_project_issue(
        context.project, gl_project_loaded, gl_issue_manager,
    )

    issue = Issue.objects.first()

    assert issue is not None

    gl_checkers.check_issue(issue, context.gl_issue)
    gl_checkers.check_user(issue.user, context.gl_assignee)
    assert issue.milestone == milestone
