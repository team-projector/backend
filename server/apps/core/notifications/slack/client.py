from slack.errors import SlackApiError

from . import get_slack_client


class SlackClient:
    def __init__(self):
        self.client = get_slack_client()
        self.client.auth_test()

    def get_channel_user_by_email(self,
                                  email: str):
        try:
            user = self.client.users_lookupByEmail(email=email).get('user')
            return self.client.im_open(user=user.get('id')).get('channel')
        except (TypeError, SlackApiError):
            pass

    def send_message_to_channel(self,
                                channel,
                                msg: str) -> None:
        self.client.chat_postMessage(
            channel=channel,
            text=msg,
        )
