import contextlib
import json
from typing import List, Optional

from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string

from apps.core.notifications.slack.client import SlackClient
from apps.core.services.html import unescape_text
from apps.users.models import User


def send_text(user: User, msg: str, **kwargs) -> None:
    """Send plain text to user."""
    slack = _get_slack_client()
    if slack:
        slack.send_text(user, msg, **kwargs)


def send_blocks(user: User, blocks: List[object], **kwargs) -> None:
    """Send rich message to user."""
    slack = _get_slack_client()
    if slack:
        slack.send_blocks(user, blocks, **kwargs)


def _get_slack_client() -> Optional[SlackClient]:
    with contextlib.suppress(ImproperlyConfigured):
        return SlackClient()

    return None


def render_blocks(template, context) -> List[object]:
    """Prepare blocks for sending to slack."""
    rendered = render_to_string(template, context)
    slack_msg = json.loads(rendered)
    unescape_text(slack_msg, "text")

    return slack_msg
