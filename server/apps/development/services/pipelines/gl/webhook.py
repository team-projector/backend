import logging
import re
import typing as ty

from constance import config

from apps.core.notifications import slack
from apps.development.services.gl.webhook import BaseGLWebhook
from apps.users.models import User

logger = logging.getLogger(__name__)

MERGE_REQUEST_ID_RE = re.compile(r"See merge request .+!([\d]+)")
MERGE_REQUEST_TITLE_RE = re.compile(r"\\nResolve\s(.*\")\\n")


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
        body_commit = body["commit"]
        need_extract = not (
            body["merge_request"]
            or not body_commit
            or not body_commit["message"]
        )

        if not need_extract:
            return None

        merge_request_id = self._get_merge_request_url(body_commit["message"])

        if not merge_request_id:
            return None

        return {
            "url": "{0}/-/merge_requests/{1}".format(
                body["project"]["web_url"],
                merge_request_id,
            ),
            "title": self._get_merge_request_title(
                body_commit["message"],
                merge_request_id,
            ),
        }

    def _get_merge_request_url(self, commit_message: str) -> ty.Optional[str]:
        merge_request_ids = re.findall(MERGE_REQUEST_ID_RE, commit_message)

        return merge_request_ids[0] if merge_request_ids else None

    def _get_merge_request_title(
        self,
        commit_message: str,
        merge_request_id: str,
    ) -> str:
        merge_request_titles = re.findall(
            MERGE_REQUEST_TITLE_RE,
            commit_message,
        )

        return (
            merge_request_titles[0]
            if merge_request_titles
            else "See merge request {0}".format(merge_request_id)
        )
