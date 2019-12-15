# -*- coding: utf-8 -*-

import pytest

from apps.users.models import User


@pytest.fixture(scope='session')
def user_admin(admin_registry):
    return admin_registry[User]
