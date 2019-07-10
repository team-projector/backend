from celery_app import app
from .services.salary.notifications import send_email_report, send_slack_report


@app.task
def send_salary_report(email: str) -> None:
    send_email_report(email)
    send_slack_report(email)
