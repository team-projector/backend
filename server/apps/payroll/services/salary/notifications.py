from apps.core.notifications.email.dispatcher import SystemEmailDispatcher
from apps.core.notifications.slack.client import SlackClient
from apps.payroll.models.salary import Salary


def is_payed(salary: Salary) -> bool:
    """Salary is payed."""
    return salary.field_tracker.has_changed("payed") and salary.payed


def send_email_report(salary: Salary) -> None:
    """Send email report."""
    if not salary.user.email:
        return

    subject = "Salary Report"
    text = "Salary has been paid."

    SystemEmailDispatcher().mail_users(
        subject=subject,
        text=text,
        recipient_list=[salary.user.email],
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
