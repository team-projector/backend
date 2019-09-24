# -*- coding: utf-8 -*-

from celery_app import app
from ..models.salary import Salary
from ..services.salary.notifications import send_email_report, send_slack_report


@app.task
def send_salary_report(salary_id: int) -> None:
    salary = Salary.objects.get(id=salary_id)

    send_email_report(salary)
    send_slack_report(salary)
