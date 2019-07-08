from apps.core.notifications.mail.dispatcher import SystemEmailDispatcher
from apps.payroll.models.salary import Salary


def send_salary_report(salary: Salary) -> None:
    send_email_report(email=salary.user.email)
    send_slack_report(email=salary.user.email)


def send_email_report(email: str) -> None:
    subject = 'Salary Report'

    text = 'Salary has been paid.'

    SystemEmailDispatcher.mail_users(
        subject=subject,
        text=text,
        recipient_list=[email]
    )


def send_slack_report(email: str) -> None:
    pass
