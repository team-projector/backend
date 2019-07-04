from apps.core.slack import get_slack_client
from apps.core.slack.base import (
    get_users_channel_by_email, send_message_to_channel
)


def send_message_to_slack(email):
    msg = 'Salary has been paid.'

    slack = get_slack_client()

    channel = get_users_channel_by_email(slack, email)

    if channel:
        send_message_to_channel(slack, channel['id'], msg)
