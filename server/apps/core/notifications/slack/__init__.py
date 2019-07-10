import slack
from django.conf import settings


def get_slack_client(token: str = None) -> slack.WebClient:
    return slack.WebClient(token or settings.SLACK_TOKEN)
