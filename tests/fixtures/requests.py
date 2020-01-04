# -*- coding: utf-8 -*-

import pytest

from tests.helpers.request_factory import RequestFactory


@pytest.fixture()  # type: ignore
def rf() -> RequestFactory:
    """Reguest factory."""
    return RequestFactory()


@pytest.fixture()  # type: ignore
def auth_rf(rf, user) -> RequestFactory:
    """Reguest factory with setted user."""
    rf.set_user(user)

    return rf
