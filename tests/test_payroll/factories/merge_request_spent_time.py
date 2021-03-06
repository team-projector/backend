import factory

from tests.test_development.factories import MergeRequestFactory
from tests.test_payroll.factories.base_spent_time import BaseSpentTimeFactory


class MergeRequestSpentTimeFactory(BaseSpentTimeFactory):
    """Merge request spent time factory."""

    base = factory.SubFactory(MergeRequestFactory)
