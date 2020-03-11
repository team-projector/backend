# -*- coding: utf-8 -*-

import factory
import pytz

from apps.payroll.models import Penalty
from tests.test_users.factories.user import UserFactory


class PenaltyFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    sum = factory.Faker("random_int")
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Penalty
