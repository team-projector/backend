# -*- coding: utf-8 -*-

import pytest

from tests.test_development.factories import TeamFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def team(user):
    """
    Team.

    :param user:
    """
    return TeamFactory.create(members=UserFactory.create_batch(2))
