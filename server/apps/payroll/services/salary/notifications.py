from apps.core.slack.client import Slack


def send_message_to_slack(email):
    msg = 'Salary has been paid.'

    slack = Slack()
    channel = slack.get_users_channel_by_email(email)

    if channel:
        slack.send_message_to_channel(channel['id'], msg)
