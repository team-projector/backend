import json
from typing import List

from django.template.loader import render_to_string

from apps.core.notifications.slack.client import SlackClient
from apps.core.services.html import unescape_text
from apps.users.models import User


def send_text(user: User, msg: str, **kwargs) -> None:
    """Send plain text to user."""
    slack = SlackClient()
    slack.send_text(user, msg, **kwargs)


def send_blocks(user: User, blocks: List[object], **kwargs) -> None:
    """Send rich message to user."""
    slack = SlackClient()
    slack.send_blocks(user, blocks, **kwargs)


def render_blocks(template, context) -> List[object]:
    """Prepare blocks for sending to slack."""
    slack_msg = json.loads(render_to_string(template, context))
    unescape_text(slack_msg, "text")

    return slack_msg
