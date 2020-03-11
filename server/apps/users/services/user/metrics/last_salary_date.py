# -*- coding: utf-8 -*-

from typing import Optional

from apps.payroll.models import Salary


def last_salary_date_resolver(parent, _, **kwargs) -> Optional[float]:
    """Returns last salary date for the user."""
    last_paid_salary = (
        Salary.objects.filter(user=parent["user"], payed=True)
        .order_by("-period_to")
        .first()
    )
    if last_paid_salary:
        return last_paid_salary.created_at

    return None
