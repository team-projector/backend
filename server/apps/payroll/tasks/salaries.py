from celery_app import app
from ..models.salary import Salary
from ..services.salary.notifications import send_email_report, send_slack_report


@app.task
def send_salary_report(salary_id: int) -> None:
    send_salary_email_report.delay(salary_id)
    send_salary_slack_report.delay(salary_id)


@app.task
def send_salary_email_report(salary_id: int) -> None:
    salary = Salary.objects.get(id=salary_id)

    send_email_report(salary)


@app.task
def send_salary_slack_report(salary_id: int) -> None:
    salary = Salary.objects.get(id=salary_id)

    send_slack_report(salary)
