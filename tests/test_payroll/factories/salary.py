import factory

from apps.payroll.models import Salary
from tests.test_users.factories.user import UserFactory


class SalaryFactory(factory.django.DjangoModelFactory):
    """Salary factory."""

    class Meta:
        model = Salary

    created_by = factory.SubFactory(UserFactory)
