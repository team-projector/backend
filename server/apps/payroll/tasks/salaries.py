# -*- coding: utf-8 -*-

from apps.payroll.models import Salary
from apps.payroll.services.salary.notifications import (
    send_email_report,
    send_slack_report,
)
from celery_app import app


@app.task
def send_salary_report_task(salary_id: int) -> None:
    """Send salary report."""
    send_salary_email_report_task.delay(salary_id)
    send_salary_slack_report_task.delay(salary_id)


@app.task
def send_salary_email_report_task(salary_id: int) -> None:
    """Send salary email report."""
    salary = Salary.objects.get(id=salary_id)

    send_email_report(salary)


@app.task
def send_salary_slack_report_task(salary_id: int) -> None:
    """Send salary slack report."""
    salary = Salary.objects.get(id=salary_id)

    send_slack_report(salary)
