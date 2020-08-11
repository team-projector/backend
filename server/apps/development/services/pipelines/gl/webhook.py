# -*- coding: utf-8 -*-

import html
import json
import logging
from typing import Optional

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

        user = self._get_user(body)
        if not user:
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
            user, html.escape(json.loads(rendered)), icon_emoji=":gitlab:",
        )

    def _get_user(self, source) -> Optional[User]:
        user = User.objects.filter(email=source["user"]["email"]).first()
        if user and user.is_active and user.notify_pipeline_status:
            return user

        return None
