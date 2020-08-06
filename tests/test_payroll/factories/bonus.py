# -*- coding: utf-8 -*-

import factory
import pytz

from apps.payroll.models import Bonus
from tests.test_users.factories.user import UserFactory


class BonusFactory(factory.django.DjangoModelFactory):
    """Bonus factory."""

    class Meta:
        model = Bonus

    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    sum = factory.Faker("random_int")  # noqa: WPS125, A003
    created_by = factory.SubFactory(UserFactory)
