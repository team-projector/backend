# -*- coding: utf-8 -*-

import pytest

from tests.helpers.base import Client


@pytest.fixture()  # delete
def admin_client(admin_user):
    return Client(admin_user)


@pytest.fixture(scope="module")  # delete
def client():
    return Client()
