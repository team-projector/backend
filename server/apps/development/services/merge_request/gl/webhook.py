# -*- coding: utf-8 -*-

import logging

from apps.core.activity.verbs import ACTION_GITLAB_WEBHOOK_TRIGGERED
from apps.core.tasks import add_action_task
from apps.development.services.gl.webhook import GLWebhook
from apps.development.tasks import sync_project_merge_request_task

logger = logging.getLogger(__name__)


class MergeRequestsGLWebhook(GLWebhook):
    """Merge request GitLab webhook handler."""

    object_kind = "merge_request"

    def handle_hook(self, body) -> None:
        """Webhook handler."""
        project_id = body["project"]["id"]
        merge_request_id = body["object_attributes"]["iid"]

        sync_project_merge_request_task.delay(project_id, merge_request_id)

        logger.info(
            "gitlab webhook was triggered: project = %s, merge_request = %s",
            project_id,
            merge_request_id,
        )

        add_action_task.delay(verb=ACTION_GITLAB_WEBHOOK_TRIGGERED)
