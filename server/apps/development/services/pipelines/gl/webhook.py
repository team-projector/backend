import logging
import re
import typing as ty

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

        slack.send_blocks_template(
            user,
            "slack/pipeline_status_changed.json",
            self.get_context(body),
            icon_emoji=":gitlab:",
        )

    def get_context(self, body) -> ty.Dict[str, object]:
        """Get context for template."""
        return {
            "gitlab_address": config.GITLAB_ADDRESS,
            "pipeline": body["object_attributes"],
            "project": body["project"],
            "commit": body["commit"],
            "merge_request": self._extract_merge_request(body),
            "gl_user": body["user"],
        }

    def _get_user(self, source) -> ty.Optional[User]:
        """
        Get user.

        :param source:
        :rtype: Optional[User]
        """
        user = User.objects.filter(email=source["user"]["email"]).first()
        if user and user.is_active and user.notify_pipeline_status:
            return user

        return None

    def _extract_merge_request(self, body) -> ty.Optional[ty.Dict[str, str]]:
        """Closes #713 See merge request junte/team-projector/backend!576."""
        if body["merge_request"]:
            return body["merge_request"]

        body_commit = body["commit"]
        if not body_commit or not body_commit["message"]:
            return None

        commit_message = body_commit["message"]
        merge_request_ids = re.findall(
            re.compile(r"See merge request .+!([\d]+)"),
            commit_message,
        )

        if not merge_request_ids:
            return None

        merge_request_url = "{0}/-/merge_requests/{1}".format(
            body["project"]["web_url"],
            merge_request_ids[0],
        )

        return {
            "url": merge_request_url,
            "title": "See merge request {0}".format(merge_request_ids[0]),
        }
