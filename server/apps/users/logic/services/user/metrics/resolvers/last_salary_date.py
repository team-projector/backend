from apps.payroll.models import Salary
from apps.users.models import User


def last_salary_date_resolver(user: User):
    """Returns last salary date for the user."""
    last_paid_salary = (
        Salary.objects.filter(user=user).order_by("-period_to").first()
    )
    if last_paid_salary:
        return last_paid_salary.period_to

    return None
