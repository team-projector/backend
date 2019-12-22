# -*- coding: utf-8 -*-

import pytest

from apps.payroll.models import Salary


@pytest.fixture(scope='session')
def salary_admin(admin_registry):
    return admin_registry[Salary]
