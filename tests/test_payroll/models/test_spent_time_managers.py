import pytest
from django.db.models import Sum
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.payroll.models import SpentTime


@pytest.fixture
def user(db):
    yield UserFactory.create(hour_rate=100)


def test_paid(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)
    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=1),
    )

    queryset = SpentTime.objects.annotate_payrolls(payroll=False)
    total_paid = queryset.aggregate(
        total_paid=Sum('paid')
    )['total_paid']

    assert total_paid == 2 * user.hour_rate


def test_payroll_metrics(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-seconds(hours=1),
    )

    queryset = SpentTime.objects.annotate_payrolls(paid=False)
    total_payroll = queryset.aggregate(
        total_payroll=Sum('payroll')
    )['total_payroll']

    assert total_payroll == 2 * user.hour_rate
