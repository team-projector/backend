# -*- coding: utf-8 -*-

import logging

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action_task
from apps.development.services.gl.webhook import GLWebhook
from apps.development.tasks import sync_project_issue_task

logger = logging.getLogger(__name__)


class NotesGLWebhook(GLWebhook):
    """Issue GitLab webhook handler."""

    object_kind = "note"
    settings_field = "note_events"

    def handle_hook(self, body) -> None:
        """Webhook handler."""
        issue = body.get("issue")
        if not issue:
            return None

        project_id = body["project"]["id"]
        sync_project_issue_task.delay(project_id, issue["id"])

        logger.info(
            "gitlab webhook was triggered: project = {0}, issue = {1}".format(
                project_id, issue["id"],
            ),
        )

        add_action_task.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
