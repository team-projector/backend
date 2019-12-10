# -*- coding: utf-8 -*-

from contextlib import suppress

from slack.errors import SlackApiError

from apps.core.notifications.slack import get_slack_client


class SlackClient:
    """A class representing client for Slack."""

    def __init__(self):
        """Initialize self."""
        self._client = get_slack_client()

    def get_channel_user_by_email(self, email: str):
        """
        Get channel by email.

        https://api.slack.com/methods/users.lookupByEmail
        """
        with suppress(TypeError, SlackApiError):
            return self._client.im_open(
                user=self._client.users_lookupByEmail(
                    email=email,
                ).get('user').get('id'),
            ).get('channel')

    def send_message_to_channel(
        self,
        channel,
        msg: str,
        **kwargs,
    ) -> None:
        """
        Send message to channel.

        https://api.slack.com/methods/chat.postMessage
        """
        self._client.chat_postMessage(
            channel=channel,
            text=msg,
            **kwargs,
        )
