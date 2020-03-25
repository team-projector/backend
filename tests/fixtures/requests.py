# -*- coding: utf-8 -*-

import pytest

from tests.helpers.api_request_factory import ApiRequestFactory
from tests.helpers.request_factory import RequestFactory


@pytest.fixture()  # type: ignore
def rf() -> RequestFactory:
    """Request factory."""
    return RequestFactory()


@pytest.fixture()  # type: ignore
def auth_rf(rf, user) -> RequestFactory:
    """Request factory with setted user."""
    rf.set_user(user)

    return rf


@pytest.fixture()  # type: ignore
def api_rf() -> ApiRequestFactory:
    """Api request factory."""
    return ApiRequestFactory()
#
#
# @pytest.fixture()
# def admin_client(db, admin_user):
#     """A Django test client logged in as an admin user."""
#     from django.test.client import Client
#
#     client = Client()
#     client.login(username=admin_user.login, password="password")
#     return client
