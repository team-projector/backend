# -*- coding: utf-8 -*-

from contextlib import suppress
from typing import List

from slack.errors import SlackApiError

from apps.core.notifications.slack import get_slack_client
from apps.users.models import User


class SlackClient:
    """A class representing client for Slack."""

    def __init__(self):
        """Initialize self."""
        self._client = get_slack_client()

    def send_text(self, user: User, msg: str, **kwargs) -> None:
        """
        Send plain text to user.

         https://api.slack.com/methods/chat.postMessage
        """
        channel = self._get_channel_user_by_email(user.email)
        if channel:
            self._client.chat_postMessage(
                channel=channel["id"], text=msg, **kwargs,
            )

    def send_blocks(self, user: User, blocks: List[object], **kwargs) -> None:
        """
        Send plain text to user.

         https://api.slack.com/methods/chat.postMessage
        """
        channel = self._get_channel_user_by_email(user.email)
        if channel:
            self._client.chat_postMessage(
                channel=channel["id"], blocks=blocks, **kwargs,
            )

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
