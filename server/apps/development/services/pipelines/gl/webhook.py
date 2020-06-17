# -*- coding: utf-8 -*-

import json
import logging

from django.conf import settings
from django.template.loader import render_to_string

from apps.core.notifications.slack.client import SlackClient
from apps.development.services.gl.webhook import GLWebhook
from apps.users.models import User

logger = logging.getLogger(__name__)


class PipelineGLWebhook(GLWebhook):
    """Pipeline GitLab webhook handler."""

    object_kind = "pipeline"
    settings_field = "pipeline_events"

    def handle_hook(self, body) -> None:
        """Webhook handler."""
        pipeline = body["object_attributes"]
        if pipeline["status"] not in {"success", "failed"}:
            return

        logger.info(
            "gitlab pipeline webhook was triggered: pipeline = {0}".format(
                pipeline["id"],
            ),
        )

        user = User.objects.get(email=body["user"]["email"])
        if not user.is_active or not user.notify_pipeline_status:
            return

        rendered = render_to_string(
            "slack/pipeline.json",
            {
                "gitlab_address": settings.GITLAB_ADDRESS,
                "pipeline": pipeline,
                "project": body["project"],
                "commit": body["commit"],
                "merge_request": body["merge_request"],
                "gl_user": body["user"],
            },
        )

        slack = SlackClient()
        slack.send_blocks(
            user, json.loads(rendered), icon_emoji=":gitlab:",
        )
