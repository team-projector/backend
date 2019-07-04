from django.template.loader import render_to_string

from apps.core.system_email_dispatcher import SystemEmailDispatcher


def send_report_to_email(salary):
    subject = f'Salary Report {salary.period_to}'

    text = render_to_string(
        'emails/salary_report.txt',
        {'salary': salary}
    )

    SystemEmailDispatcher.mail_managers(subject, text)
