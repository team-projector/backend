import factory
import pytz

from apps.payroll.models import SpentTime


class BaseSpentTimeFactory(factory.django.DjangoModelFactory):
    """Base spent time factory."""

    class Meta:
        model = SpentTime

    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    hour_rate = factory.Faker("random_int")
    time_spent = factory.Faker("random_int")
