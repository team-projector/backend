import factory
import pytz

from apps.development.tests.factories import IssueFactory
from apps.payroll.models import SpentTime


class IssueSpentTimeFactory(factory.django.DjangoModelFactory):
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    base = factory.SubFactory(IssueFactory)

    class Meta:
        model = SpentTime
