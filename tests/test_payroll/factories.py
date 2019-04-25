import factory
import pytz

from tests.test_development.factories import IssueFactory
from apps.payroll.models import SpentTime, Penalty, Bonus, Salary, WorkBreak
from tests.test_users.factories import UserFactory


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


class WorkBreakFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    reason = 'dayoff'
    from_date = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    to_date = factory.Faker('date_time_this_year', before_now=False, after_now=True, tzinfo=pytz.UTC)
    comment = factory.Faker('text', max_nb_chars=200)
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)

    class Meta:
        model = WorkBreak
