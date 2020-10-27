from typing import List, Optional

from constance import config
from django.core.mail import send_mail


def mail_users(
    subject: str,
    text: str,
    recipient_list: List[str],
    html_message: Optional[str] = None,
) -> None:
    """
    Send email.

    Sending text in two formats: simple and html.
    """
    send_mail(
        subject=subject,
        message=text,
        from_email=config.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
    )
