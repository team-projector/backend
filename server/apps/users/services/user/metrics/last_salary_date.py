from apps.payroll.models import Salary


def last_salary_date_resolver(user):
    """Returns last salary date for the user."""
    if user.is_authenticated:
        last_paid_salary = (
            Salary.objects.filter(user=user).order_by("-period_to").first()
        )
        if last_paid_salary:
            return last_paid_salary.period_to

    return None
