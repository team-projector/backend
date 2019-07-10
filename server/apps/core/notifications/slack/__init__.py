import slack
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_slack_client() -> slack.WebClient:
    token = settings.SLACK_TOKEN
    if not token:
        raise ImproperlyConfigured('"settings.SLACK_TOKEN" must be filled')

    return slack.WebClient(settings.SLACK_TOKEN)
