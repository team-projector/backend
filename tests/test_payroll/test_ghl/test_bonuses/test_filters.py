# -*- coding: utf-8 -*-

from apps.payroll.graphql.filters import BonusFilterSet
from apps.payroll.models import Bonus
from tests.test_payroll.factories import BonusFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_bonuses_filter_by_user(user):
    """
    Test bonuses filter by user.

    :param user:
    """
    BonusFactory.create_batch(size=3, user=user)

    user2 = UserFactory.create()
    bonuses_user2 = BonusFactory.create_batch(size=5, user=user2)

    queryset = BonusFilterSet(
        data={"user": user2.id},
        queryset=Bonus.objects.all(),
    ).qs

    assert queryset.count() == 5
    assert set(queryset) == set(bonuses_user2)


def test_bonuses_filter_by_salary(user):
    """
    Test bonuses filter by salary.

    :param user:
    """
    salary = SalaryFactory(user=user)
    BonusFactory.create_batch(size=3, user=user)
    bonuses_salary2 = BonusFactory.create_batch(
        size=5,
        user=user,
        salary=salary,
    )

    queryset = BonusFilterSet(
        data={"salary": salary.id},
        queryset=Bonus.objects.all(),
    ).qs

    assert queryset.count() == 5
    assert set(queryset) == set(bonuses_salary2)
