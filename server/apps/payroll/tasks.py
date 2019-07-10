from celery_app import app
from .services.salary.notifications import send_email_report, send_slack_report
from .models.salary import Salary


@app.task
def send_salary_report(salary_id: int) -> None:
    salary = Salary.objects.get(id=salary_id)

    send_email_report(salary)
    send_slack_report(salary)
