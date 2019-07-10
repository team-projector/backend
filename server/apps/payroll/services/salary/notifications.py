from apps.core.notifications.mail.dispatcher import SystemEmailDispatcher
from apps.core.notifications.slack.client import SlackClient
from apps.payroll.models.salary import Salary


def send_email_report(salary: Salary) -> None:
    subject = 'Salary Report'
    text = 'Salary has been paid.'

    SystemEmailDispatcher.mail_users(
        subject=subject,
        text=text,
        recipient_list=[salary.user.email]
    )


def send_slack_report(salary: Salary) -> None:
    msg = 'Salary has been paid.'

    slack = SlackClient()
    channel = slack.get_channel_user_by_email(salary.user.email)

    if channel:
        slack.send_message_to_channel(channel['id'], msg)


def is_payed(salary: Salary) -> bool:
    return salary.field_tracker.has_changed('payed') and salary.payed
