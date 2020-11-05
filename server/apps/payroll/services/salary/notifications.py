from typing import Dict

from constance import config
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.notifications.email.dispatcher import mail_users
from apps.core.notifications.slack.client import SlackClient
from apps.core.utils.mail import render_email_html
from apps.development.models import Issue, MergeRequest
from apps.payroll.models.salary import Salary


def is_payed(salary: Salary) -> bool:
    """Salary is payed."""
    return salary.field_tracker.has_changed("payed") and salary.payed


def send_email_report(salary: Salary) -> None:
    """Send email report."""
    if not salary.user.email:
        return

    subject = "Salary report"
    text = "Salary has been paid."

    mail_users(
        subject=subject,
        text=text,
        recipient_list=[salary.user.email],
        html_message=render_email_html(
            "email/salary_email.html",
            {
                "title": subject,
                "salary": salary,
                "currency": config.CURRENCY_CODE.label,
                "spend_data": _get_spend_data(salary),
                "domain": settings.DOMAIN_NAME,
            },
        ),
    )


def send_slack_report(salary: Salary) -> None:
    """Send slack report."""
    if not salary.user.email:
        return

    msg = "Salary has been paid."

    slack = SlackClient()
    slack.send_text(
        salary.user,
        msg,
        icon_emoji=":moneybag:",
    )


def _get_spend_data(salary) -> Dict[str, Dict[str, float]]:
    """Get spend data for salary."""
    return {
        "issues": _get_spend_data_for_model(salary, Issue),
        "merge_requests": _get_spend_data_for_model(salary, MergeRequest),
    }


def _get_spend_data_for_model(salary, model) -> Dict[str, float]:
    """Get spend data for salary by base model."""
    return salary.payrolls.filter(
        spenttime__content_type=ContentType.objects.get_for_model(model),
    ).aggregate(
        total_sum=models.Sum("spenttime__sum"),
        total_time_spent=models.Sum("spenttime__time_spent"),
    )
