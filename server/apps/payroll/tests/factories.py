import factory
import pytz

from apps.development.tests.factories import IssueFactory
from apps.payroll.models import SpentTime, Penalty, Bonus, Salary
from apps.users.tests.factories import UserFactory


class IssueSpentTimeFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    base = factory.SubFactory(IssueFactory)

    class Meta:
        model = SpentTime


class PenaltyFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    sum = factory.Faker('random_int')
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Penalty


class BonusFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    sum = factory.Faker('random_int')
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Bonus


class SalaryFactory(factory.django.DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Salary
