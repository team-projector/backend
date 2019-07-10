from apps.core.notifications.mail.dispatcher import SystemEmailDispatcher
from apps.core.notifications.slack.client import SlackClient
from apps.payroll.models.salary import Salary


def is_payed(salary: Salary) -> bool:
    return salary.field_tracker.has_changed('payed') and salary.payed


def send_email_report(email: str) -> None:
    subject = 'Salary Report'
    text = 'Salary has been paid.'

    SystemEmailDispatcher.mail_users(
        subject=subject,
        text=text,
        recipient_list=[email]
    )


def send_slack_report(email: str) -> None:
    msg = 'Salary has been paid.'

    slack = SlackClient()
    channel = slack.get_channel_user_by_email(email)

    if channel:
        slack.send_message_to_channel(channel['id'], msg)
