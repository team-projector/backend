from contextlib import suppress
from typing import List

import slack
from constance import config
from django.core.exceptions import ImproperlyConfigured
from slack.errors import SlackApiError

from apps.core.notifications.slack.decorators import error_handler
from apps.users.models import User


class SlackClient:
    """A class representing client for Slack."""

    def __init__(self):
        """Initialize self."""
        self._client = self._get_slack_client()

    @error_handler
    def send_text(self, user: User, msg: str, **kwargs) -> None:
        """
        Send plain text to user.

         https://api.slack.com/methods/chat.postMessage
        """
        channel = self._get_channel_user_by_email(user.email)
        if channel:
            self._client.chat_postMessage(
                channel=channel["id"],
                text=msg,
                **kwargs,
            )

    @error_handler
    def send_blocks(self, user: User, blocks: List[object], **kwargs) -> None:
        """
        Send plain text to user.

         https://api.slack.com/methods/chat.postMessage
        """
        channel = self._get_channel_user_by_email(user.email)
        if channel:
            self._client.chat_postMessage(
                channel=channel["id"],
                blocks=blocks,
                **kwargs,
            )

    def _get_slack_client(self) -> slack.WebClient:  # type: ignore
        """
        Get slack client.

        :rtype: slack.WebClient
        """
        token = config.SLACK_TOKEN
        if not token:
            raise ImproperlyConfigured("'settings.SLACK_TOKEN' must be filled")

        return slack.WebClient(token)  # type: ignore

    def _get_channel_user_by_email(self, email: str):
        """
        Get channel by email.

        https://api.slack.com/methods/users.lookupByEmail
        """
        with suppress(TypeError, SlackApiError):
            return self._client.im_open(
                user=self._client.users_lookupByEmail(email=email)
                .get("user")
                .get("id"),
            ).get("channel")
