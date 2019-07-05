from apps.core.system_email_dispatcher import SystemEmailDispatcher


def send_report_to_email(salary, email):
    subject = f'Salary Report {salary.period_to}'

    text = 'Salary has been paid.'

    SystemEmailDispatcher.mail_users(
        subject=subject,
        text=text,
        recipient_list=[email]
    )
