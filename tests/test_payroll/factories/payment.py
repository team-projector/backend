import factory
import pytz

from apps.payroll.models import Payment
from tests.test_users.factories.user import UserFactory


class PaymentFactory(factory.django.DjangoModelFactory):
    """Payment factory."""

    class Meta:
        model = Payment

    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    sum = factory.Faker("random_int")  # noqa: WPS125, A003
    created_by = factory.SubFactory(UserFactory)
