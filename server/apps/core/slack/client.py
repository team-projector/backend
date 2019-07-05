from . import get_slack_client


class Slack:
    def __init__(self):
        self.client = get_slack_client()

    def get_users_channel_by_email(self, email):
        user = self.client.users_lookupByEmail(email=email).get('user')

        if user:
            return self.client.im_open(user=user.get('id')).get('channel')

    def send_message_to_channel(self, channel, msg):
        return self.client.chat_postMessage(
            channel=channel,
            text=msg,
        )
