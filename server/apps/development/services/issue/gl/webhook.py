# -*- coding: utf-8 -*-

import logging

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action_task
from apps.development.services.gl.webhook import GLWebhook
from apps.development.tasks import sync_project_issue_task

logger = logging.getLogger(__name__)


class IssuesGLWebhook(GLWebhook):
    """Issue GitLab webhook handler."""

    object_kind = "issue"
    settings_field = "issues_events"

    def handle_hook(self, body) -> None:
        """Webhook handler."""
        project_id = body["project"]["id"]
        issue_id = body["object_attributes"]["iid"]

        sync_project_issue_task.delay(project_id, issue_id)

        logger.info(
            "gitlab webhook was triggered: project = {0}, issue = {1}".format(
                project_id, issue_id,
            ),
        )

        add_action_task.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
