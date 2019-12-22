# -*- coding: utf-8 -*-

import factory

from apps.payroll.models import Salary
from tests.test_users.factories.user import UserFactory


class SalaryFactory(factory.django.DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Salary
