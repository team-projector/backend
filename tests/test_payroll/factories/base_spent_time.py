# -*- coding: utf-8 -*-

import factory
import pytz

from apps.payroll.models import SpentTime


class BaseSpentTimeFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    rate = factory.Faker("random_int")
    time_spent = factory.Faker("random_int")

    class Meta:
        model = SpentTime
