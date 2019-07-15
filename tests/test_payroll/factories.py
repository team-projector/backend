import random

import factory
import pytz

from apps.payroll.models import Bonus, Payment, Penalty, Salary, SpentTime, WorkBreak
from apps.payroll.models.workbreak import DAYOFF, VACATION, DISEASE
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_users.factories import UserFactory


class BaseSpentTimeFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)
    rate = factory.Faker('random_int')
    time_spent = factory.Faker('random_int')

    class Meta:
        model = SpentTime


class IssueSpentTimeFactory(BaseSpentTimeFactory):
    base = factory.SubFactory(IssueFactory)


class MergeRequestSpentTimeFactory(BaseSpentTimeFactory):
    base = factory.SubFactory(MergeRequestFactory)


class PenaltyFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)
    sum = factory.Faker('random_int')
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Penalty


class BonusFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)
    sum = factory.Faker('random_int')
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Bonus


class SalaryFactory(factory.django.DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Salary


class WorkBreakFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    reason = random.choice((DAYOFF, VACATION, DISEASE))
    from_date = factory.Faker('date_time_this_year', before_now=True,
                              after_now=False, tzinfo=pytz.UTC)
    to_date = factory.Faker('date_time_this_year', before_now=False,
                            after_now=True, tzinfo=pytz.UTC)
    comment = factory.Faker('text', max_nb_chars=200)
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)

    class Meta:
        model = WorkBreak


class PaymentFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)
    sum = factory.Faker('random_int')
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Payment
