from datetime import timedelta

from apps.development.models.issue import Issue, IssueState
from apps.payroll.models import SpentTime
from apps.payroll.services.salary.calculator import SalaryCalculator
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def add_issue(project, milestone=None, const=1) -> Issue:
    """Create issue."""
    return IssueFactory.create(
        project=project,
        milestone=milestone,
        state=IssueState.CLOSED,
        time_estimate=const * 100,
        total_time_spent=const * 50,
    )


def add_spent_time(base, user, time_spent) -> SpentTime:
    """Add spent time for issue."""
    return IssueSpentTimeFactory.create(
        user=user,
        base=base,
        time_spent=time_spent,
    )


def generate_payroll(user, payroll_date) -> None:
    """Generate salary for user."""
    calculator = SalaryCalculator(
        user,
        (payroll_date - timedelta(days=1)).date(),
        (payroll_date + timedelta(days=1)).date(),
    )

    calculator.generate(user)
