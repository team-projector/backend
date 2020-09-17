# -*- coding: utf-8 -*-

import pytest
from django.db.models import Sum
from jnt_django_toolbox.helpers.time import seconds

from apps.payroll.models import SpentTime
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    return UserFactory.create(hour_rate=100)


def test_paid(user):
    """
    Test paid.

    :param user:
    """
    issue = IssueFactory.create(user=user)
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

    total_paid = SpentTime.objects.annotate_payrolls(payroll=False).aggregate(
        total_paid=Sum("paid"),
    )["total_paid"]

    assert total_paid == 2 * user.hour_rate


def test_payroll_metrics(user):
    """
    Test payroll metrics.

    :param user:
    """
    issue = IssueFactory.create(user=user)

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

    total_payroll = SpentTime.objects.annotate_payrolls(paid=False).aggregate(
        total_payroll=Sum("payroll"),
    )["total_payroll"]

    assert total_payroll == 2 * user.hour_rate
