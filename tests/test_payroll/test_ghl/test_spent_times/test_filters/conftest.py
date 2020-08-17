# -*- coding: utf-8 -*-

import pytest

from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


@pytest.fixture()
def user2(db):
    """
    User2.

    :param db:
    """
    return UserFactory.create()


@pytest.fixture()
def issue(db):
    """
    Issue.

    :param db:
    """
    return IssueFactory.create()


@pytest.fixture()
def salary(db, user):
    """
    Salary.

    :param db:
    :param user:
    """
    return SalaryFactory.create(user=user)
