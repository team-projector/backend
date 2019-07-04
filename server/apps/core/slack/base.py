def get_users_channel_by_email(slack, email):
    user = slack.users_lookupByEmail(email=email).get('user')

    if user:
        return slack.im_open(user=user.get('id')).get('channel')


def send_message_to_channel(slack, channel, msg):
    return slack.chat_postMessage(
        channel=channel,
        text=msg,
    )
