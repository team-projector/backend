# -*- coding: utf-8 -*-

import factory

from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories.base_spent_time import BaseSpentTimeFactory


class IssueSpentTimeFactory(BaseSpentTimeFactory):
    base = factory.SubFactory(IssueFactory)
