from apps.core.notifications.slack.client import SlackClient
from apps.payroll.models.salary import Salary


def send_salary_report(salary: Salary) -> None:
    send_slack_report(salary)


def send_slack_report(salary: Salary) -> None:
    msg = 'Salary has been paid.'

    slack = SlackClient()
    channel = slack.get_channel_user_by_email(salary.user.email)

    if channel:
        slack.send_message_to_channel(channel['id'], msg)


def is_payed(salary: Salary) -> bool:
    return salary.payed_tracker.changed().get('payed') is False
