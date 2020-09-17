# -*- coding: utf-8 -*-

import pytest
from rest_framework.exceptions import AuthenticationFailed

from apps.development.models import Issue
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlIssueWebhookFactory,
)
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory


@pytest.fixture(autouse=True)
def _gitlab_webhook_secret_token(override_config) -> None:
    """Set test gitlab token."""
    with override_config(GITLAB_WEBHOOK_SECRET_TOKEN="SECRET_TOKEN"):
        yield


def test_no_token(api_rf, gl_webhook_view):
    """
    Test no token.

    :param api_rf:
    :param gl_webhook_view:
    """
    webhook = GlIssueWebhookFactory.create()

    with pytest.raises(AuthenticationFailed):
        gl_webhook_view(api_rf.post("/", data=webhook, format="json"))


def test_bad_token(api_rf, gl_webhook_view):
    """
    Test bad token.

    :param api_rf:
    :param gl_webhook_view:
    """
    webhook = GlIssueWebhookFactory.create()

    with pytest.raises(AuthenticationFailed):
        gl_webhook_view(
            api_rf.post(
                "/",
                data=webhook,
                format="json",
                HTTP_X_GITLAB_TOKEN="BAD_TOKEN",
            ),
        )


def test_sync_with_secret_token(db, gl_mocker, gl_webhook_view, api_rf):
    """
    Test sync with secret token.

    :param db:
    :param gl_mocker:
    :param gl_webhook_view:
    :param api_rf:
    """
    project, gl_project = initializers.init_project()
    gl_assignee = GlUserFactory.create()
    gl_issue = GlIssueFactory.create(
        project_id=gl_project["id"],
        assignee=gl_assignee,
    )
    webhook_data = GlIssueWebhookFactory.create(
        project=gl_project,
        object_attributes=gl_issue,
    )

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        issues=[gl_issue],
    )
    gl_mock.mock_issue_endpoints(gl_mocker, gl_project, gl_issue)

    gl_webhook_view(
        api_rf.post(
            "/",
            data=webhook_data,
            format="json",
            HTTP_X_GITLAB_TOKEN="SECRET_TOKEN",
        ),
    )

    assert Issue.objects.count() == 1

    issue = Issue.objects.first()

    gl_checkers.check_issue(issue, gl_issue)
    gl_checkers.check_user(issue.user, gl_assignee)
