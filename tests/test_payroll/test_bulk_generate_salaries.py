from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.development.models import STATE_CLOSED
from tests.test_development.factories import IssueFactory
from apps.payroll.models import Salary
from tests.test_payroll.factories import IssueSpentTimeFactory
from apps.payroll.utils.salary.calculator import SalaryCalculator
from apps.users.models import User
from tests.test_users.factories import UserFactory


class BulkGenerateSalariesTests(TestCase):
    def setUp(self):
        self.initiator = User.objects.create_user(login='initiator')
        self.user = User.objects.create_user(login='user', hour_rate=100)
        self.calculator = SalaryCalculator(self.initiator,
                                           period_from=timezone.now() - timedelta(days=30),
                                           period_to=timezone.now())

    def test_single(self):
        issue = IssueFactory.create(state=STATE_CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        self.calculator.generate_bulk()

        self.assertEqual(Salary.objects.count(), 1)

        salary = Salary.objects.filter(user=self.user).first()
        self.assertEqual(salary.total, self.user.hour_rate * 4)

    def test_many(self):
        issue_1 = IssueFactory.create(state=STATE_CLOSED)
        issue_2 = IssueFactory.create(state=STATE_CLOSED)
        issue_3 = IssueFactory.create(state=STATE_CLOSED)

        user_2 = UserFactory.create()
        user_3 = UserFactory.create()

        IssueSpentTimeFactory.create(user=self.user, base=issue_1, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=user_2, base=issue_2, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=user_3, base=issue_3, time_spent=timedelta(hours=5).total_seconds())

        self.calculator.generate_bulk()

        self.assertEqual(Salary.objects.count(), 3)

        salary = Salary.objects.filter(user=self.user).first()
        self.assertEqual(salary.total, self.user.hour_rate)

        salary = Salary.objects.filter(user=user_2).first()
        self.assertEqual(salary.total, user_2.hour_rate * 2)

        salary = Salary.objects.filter(user=user_3).first()
        self.assertEqual(salary.total, user_3.hour_rate * 5)
