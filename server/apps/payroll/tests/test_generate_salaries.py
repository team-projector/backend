from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.payroll.models import Payroll
from apps.payroll.tests.factories import BonusFactory, IssueSpentTimeFactory, PenaltyFactory, SalaryFactory
from apps.payroll.utils.salary.calculator import SalaryCalculator
from apps.users.models import User
from apps.users.tests.factories import UserFactory


class GenerateSalariesTests(TestCase):
    def setUp(self):
        self.initiator = User.objects.create_user(login='initiator')
        self.user = User.objects.create_user(login='user', hour_rate=100)
        self.calculator = SalaryCalculator(self.initiator,
                                           period_from=timezone.now() - timedelta(days=30),
                                           period_to=timezone.now())

    def test_common(self):
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=5).total_seconds())

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time, timedelta(hours=4).total_seconds())
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.penalty, 0)
        self.assertEqual(salary.bonus, 0)
        self.assertEqual(salary.sum, salary.total)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 3)

    def test_with_penalty(self):
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=5).total_seconds())

        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time, timedelta(hours=4).total_seconds())
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.penalty, penalty.sum)
        self.assertEqual(salary.bonus, 0)
        self.assertEqual(salary.total, salary.sum - penalty.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 4)

    def test_with_bonus(self):
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time, timedelta(hours=4).total_seconds())
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, 0)
        self.assertEqual(salary.total, salary.sum + bonus.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 4)

    def test_with_bonus_penalty(self):
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)
        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time, timedelta(hours=4).total_seconds())
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, penalty.sum)

        self.assertEqual(salary.total, salary.sum + bonus.sum - penalty.sum)
        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 5)

    def test_some_already_with_salary(self):
        prev_salary = SalaryFactory.create(user=self.user)

        IssueSpentTimeFactory.create(salary=prev_salary, user=self.user, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(salary=prev_salary, user=self.user, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)
        PenaltyFactory.create(user=self.user, salary=prev_salary, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time, timedelta(hours=5).total_seconds())
        self.assertEqual(salary.sum, self.user.hour_rate * 5)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, 0)
        self.assertEqual(salary.total, salary.sum + bonus.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 2)
        self.assertEqual(Payroll.objects.filter(salary=prev_salary).count(), 3)

    def test_with_another_user(self):
        user_2 = UserFactory.create()

        IssueSpentTimeFactory.create(user=user_2, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=user_2, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, time_spent=timedelta(hours=5).total_seconds())

        BonusFactory.create(user=user_2)
        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time, timedelta(hours=5).total_seconds())
        self.assertEqual(salary.sum, self.user.hour_rate * 5)
        self.assertEqual(salary.bonus, 0)
        self.assertEqual(salary.penalty, penalty.sum)
        self.assertEqual(salary.total, salary.sum - penalty.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 2)
