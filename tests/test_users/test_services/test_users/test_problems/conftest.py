# -*- coding: utf-8 -*-

import pytest

from tests.test_users.factories import UserFactory


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    return UserFactory.create(daily_work_hours=8)
