# -*- coding: utf-8 -*-

from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.payroll.models import Salary
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_single(user, calculator):
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=-seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    calculator.generate_bulk()

    assert Salary.objects.count() == 1

    salary = Salary.objects.filter(user=user).first()
    assert salary.total == user.hour_rate * 4


def test_many(user, calculator):
    issues = IssueFactory.create_batch(3, state=IssueState.CLOSED)
    users = UserFactory.create_batch(2)

    IssueSpentTimeFactory.create(
        user=user, base=issues[0], time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=users[0], base=issues[1], time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=users[1], base=issues[2], time_spent=seconds(hours=5),
    )

    calculator.generate_bulk()

    assert Salary.objects.count() == 3

    salary = Salary.objects.filter(user=user).first()
    assert salary.total == user.hour_rate

    salary = Salary.objects.filter(user=users[0]).first()
    assert salary.total == users[0].hour_rate * 2

    salary = Salary.objects.filter(user=users[1]).first()
    assert salary.total == users[1].hour_rate * 5
