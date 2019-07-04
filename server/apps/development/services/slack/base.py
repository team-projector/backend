from apps.core.slack import get_slack_client


def send_msg_to_chanel(chanel, msg):
    slack = get_slack_client()

    slack.chat_postMessage(
        channel=chanel,
        text=msg,
    )
