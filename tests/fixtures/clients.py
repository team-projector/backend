# -*- coding: utf-8 -*-

import pytest
from tests.helpers.base import Client


@pytest.fixture
def admin_client(admin_user):
    return Client(admin_user)


@pytest.fixture(scope='module')
def client():
    return Client()
