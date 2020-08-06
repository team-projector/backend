# -*- coding: utf-8 -*-

import random

import factory
import pytz

from apps.payroll.models import WorkBreak
from apps.payroll.models.work_break import WorkBreakReason
from tests.test_users.factories.user import UserFactory


class WorkBreakFactory(factory.django.DjangoModelFactory):
    """Work break factory."""

    class Meta:
        model = WorkBreak

    user = factory.SubFactory(UserFactory)
    comment = factory.Faker("text", max_nb_chars=200)
    reason = random.choice(  # noqa: S311
        (
            WorkBreakReason.DAYOFF,
            WorkBreakReason.VACATION,
            WorkBreakReason.DISEASE,
        ),
    )

    from_date = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    to_date = factory.Faker(
        "date_time_this_year",
        before_now=False,
        after_now=True,
        tzinfo=pytz.UTC,
    )
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
