from apps.core.slack.base import (
    get_users_channel_by_email, send_message_to_channel
)


def send_message_to_slack(email):
    msg = 'Salary has been paid.'

    channel = get_users_channel_by_email(email)

    if channel:
        send_message_to_channel(channel['id'], msg)
