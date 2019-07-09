from apps.core.notifications.mail.dispatcher import SystemEmailDispatcher
from apps.payroll.models.salary import Salary


def send_salary_report(salary: Salary) -> None:
    send_email_report(salary)


def send_email_report(salary: Salary) -> None:
    subject = 'Salary Report'

    text = 'Salary has been paid.'

    SystemEmailDispatcher.mail_users(
        subject=subject,
        text=text,
        recipient_list=[salary.user.email]
    )


def is_payed(salary: Salary) -> bool:
    return salary.payed_tracker.changed().get('payed') is False
