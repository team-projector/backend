# -*- coding: utf-8 -*-

from apps.payroll.models import Salary


def last_salary_date_resolver(parent, info, **kwargs):  # noqa:WPS110
    """Returns last salary date for the user."""
    user = info.context.user

    if user.is_authenticated:
        last_paid_salary = (
            Salary.objects.filter(user=user).order_by("-period_to").first()
        )
        if last_paid_salary:
            return last_paid_salary.period_to

    return None
