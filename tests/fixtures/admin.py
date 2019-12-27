# -*- coding: utf-8 -*-

import pytest
from django.contrib.admin import site


@pytest.fixture(scope='session')
def admin_registry():
    return site._registry  # noqa: WPS437
