from . import get_slack_client


def get_users_channel_by_email(email):
    slack = get_slack_client()

    user = slack.users_lookupByEmail(email=email).get('user')

    if user:
        return slack.im_open(user=user.get('id')).get('channel')


def send_message_to_channel(channel, msg):
    slack = get_slack_client()

    return slack.chat_postMessage(
        channel=channel,
        text=msg,
    )
