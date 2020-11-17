import logging
from typing import Optional

from constance import config

from apps.core.notifications import slack
from apps.development.services.gl.webhook import BaseGLWebhook
from apps.users.models import User

logger = logging.getLogger(__name__)


class PipelineGLWebhook(BaseGLWebhook):
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

        blocks = slack.render_blocks(
            "slack/pipeline_status_changed.json",
            {
                "gitlab_address": config.GITLAB_ADDRESS,
                "pipeline": pipeline,
                "project": body["project"],
                "commit": body["commit"],
                "merge_request": body["merge_request"],
                "gl_user": body["user"],
            },
        )

        slack.send_blocks(user, blocks, icon_emoji=":gitlab:")

    def _get_user(self, source) -> Optional[User]:
        """
        Get user.

        :param source:
        :rtype: Optional[User]
        """
        user = User.objects.filter(email=source["user"]["email"]).first()
        if user and user.is_active and user.notify_pipeline_status:
            return user

        return None
