# -*- coding: utf-8 -*-

import factory
import pytz

from apps.payroll.models import Bonus
from tests.test_users.factories.user import UserFactory


class BonusFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    sum = factory.Faker("random_int")
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Bonus
