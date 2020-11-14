from typing import List

from apps.core.notifications.slack.client import SlackClient
from apps.users.models import User


def send_text(user: User, msg: str, **kwargs) -> None:
    """Send plain text to user."""
    slack = SlackClient()
    slack.send_text(user, msg, **kwargs)


def send_blocks(user: User, blocks: List[object], **kwargs) -> None:
    """Send rich message to user."""
    slack = SlackClient()
    slack.send_blocks(user, blocks, **kwargs)
