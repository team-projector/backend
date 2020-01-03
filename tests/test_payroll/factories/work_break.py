# -*- coding: utf-8 -*-

import random

import factory
import pytz

from apps.payroll.models import WorkBreak
from apps.payroll.models.work_break import WORK_BREAK_REASONS
from tests.test_users.factories.user import UserFactory


class WorkBreakFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    comment = factory.Faker("text", max_nb_chars=200)
    reason = random.choice((
        WORK_BREAK_REASONS.DAYOFF,
        WORK_BREAK_REASONS.VACATION,
        WORK_BREAK_REASONS.DISEASE
    ))

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

    class Meta:
        model = WorkBreak
