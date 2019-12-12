from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.payroll.models import Salary
from apps.payroll.services.salary.calculator import SalaryCalculator
from apps.users.models import User
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


class BulkGenerateSalariesTests(TestCase):
    def setUp(self):
        self.initiator = User.objects.create_user(login='initiator')
        self.user = User.objects.create_user(login='user', hour_rate=100)
        self.calculator = SalaryCalculator(self.initiator,
                                           period_from=timezone.now() - timedelta(
                                               days=30),
                                           period_to=timezone.now())

    def test_single(self):
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=seconds(hours=1))
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=-seconds(hours=2))
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=seconds(hours=5))

        self.calculator.generate_bulk()

        self.assertEqual(Salary.objects.count(), 1)

        salary = Salary.objects.filter(user=self.user).first()
        self.assertEqual(salary.total, self.user.hour_rate * 4)

    def test_many(self):
        issue_1 = IssueFactory.create(state=ISSUE_STATES.CLOSED)
        issue_2 = IssueFactory.create(state=ISSUE_STATES.CLOSED)
        issue_3 = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        user_2 = UserFactory.create()
        user_3 = UserFactory.create()

        IssueSpentTimeFactory.create(user=self.user, base=issue_1,
                                     time_spent=seconds(hours=1))
        IssueSpentTimeFactory.create(user=user_2, base=issue_2,
                                     time_spent=seconds(hours=2))
        IssueSpentTimeFactory.create(user=user_3, base=issue_3,
                                     time_spent=seconds(hours=5))

        self.calculator.generate_bulk()

        self.assertEqual(Salary.objects.count(), 3)

        salary = Salary.objects.filter(user=self.user).first()
        self.assertEqual(salary.total, self.user.hour_rate)

        salary = Salary.objects.filter(user=user_2).first()
        self.assertEqual(salary.total, user_2.hour_rate * 2)

        salary = Salary.objects.filter(user=user_3).first()
        self.assertEqual(salary.total, user_3.hour_rate * 5)
