from slack.errors import SlackApiError

from . import get_slack_client


class SlackClient:
    def __init__(self):
        self.client = get_slack_client()

    def get_channel_user_by_email(self,
                                  email: str):
        try:
            return self.client.im_open(
                user=self.client.users_lookupByEmail(
                    email=email
                ).get('user').get('id')
            ).get('channel')
        except (TypeError, SlackApiError):
            pass

    def send_message_to_channel(self,
                                channel,
                                msg: str,
                                **kwargs) -> None:
        self.client.chat_postMessage(
            channel=channel,
            text=msg,
            **kwargs,
        )
