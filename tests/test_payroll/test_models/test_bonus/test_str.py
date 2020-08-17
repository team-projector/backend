# -*- coding: utf-8 -*-

from tests.test_payroll.factories import BonusFactory


def test_str(user):
    """
    Test str.

    :param user:
    """
    bonus = BonusFactory.create(user=user, sum=150)

    assert str(bonus) == "{0} [{1}]: 150".format(user.login, bonus.created_at)
