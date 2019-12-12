from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.development.models.issue import ISSUE_STATES
from apps.payroll.models import Payroll, Salary
from apps.payroll.services.salary.calculator import SalaryCalculator
from apps.payroll.services.salary.exceptions import EmptySalaryException
from apps.users.models import User
from apps.core.utils.time import seconds
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    BonusFactory, IssueSpentTimeFactory,
    PenaltyFactory, SalaryFactory, MergeRequestSpentTimeFactory
)
from tests.test_users.factories.user import UserFactory


class GenerateSalariesTests(TestCase):
    def setUp(self):
        self.initiator = User.objects.create_user(login='initiator')
        self.user = User.objects.create_user(
            login='user',
            hour_rate=100
        )
        self.calculator = SalaryCalculator(
            self.initiator,
            period_from=timezone.now() - timedelta(days=30),
            period_to=timezone.now()
        )

    def test_common(self):
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)
        mr = MergeRequestFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        MergeRequestSpentTimeFactory.create(user=self.user, base=mr,
                                            time_spent=timedelta(
                                                hours=5).total_seconds())

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=9))
        self.assertEqual(self.user.hour_rate * 9, salary.sum)
        self.assertEqual(0, salary.penalty)
        self.assertEqual(0, salary.bonus)
        self.assertEqual(0, salary.taxes)

        self.assertEqual(salary.total, salary.sum)

        self.assertEqual(4, Payroll.objects.filter(salary=salary).count())

    def test_no_payrolls(self):
        salary = None

        with self.assertRaises(EmptySalaryException):
            salary = self.calculator.generate(self.user)

        self.assertIsNone(salary)
        self.assertEqual(Salary.objects.count(), 0)

    def test_with_penalty(self):
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=4))
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.penalty, penalty.sum)
        self.assertEqual(salary.bonus, 0)
        self.assertEqual(salary.taxes, 0)
        self.assertEqual(salary.total, salary.sum - penalty.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 4)

    def test_with_bonus(self):
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=4))
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, 0)
        self.assertEqual(salary.taxes, 0)
        self.assertEqual(salary.total, salary.sum + bonus.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 4)

    def test_complex(self):
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)
        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=4))
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, penalty.sum)
        self.assertEqual(salary.taxes, 0)

        self.assertEqual(salary.total, salary.sum + bonus.sum - penalty.sum)
        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 5)

    def test_some_already_with_salary(self):
        prev_salary = SalaryFactory.create(user=self.user)
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(salary=prev_salary, base=issue,
                                     user=self.user,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(salary=prev_salary, base=issue,
                                     user=self.user,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)
        PenaltyFactory.create(user=self.user, salary=prev_salary, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=5))
        self.assertEqual(salary.sum, self.user.hour_rate * 5)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, 0)
        self.assertEqual(salary.taxes, 0)
        self.assertEqual(salary.total, salary.sum + bonus.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 2)
        self.assertEqual(Payroll.objects.filter(salary=prev_salary).count(), 3)

    def test_with_another_user(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=user_2, base=issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=user_2, base=issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        BonusFactory.create(user=user_2)
        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=5))
        self.assertEqual(salary.sum, self.user.hour_rate * 5)
        self.assertEqual(salary.bonus, 0)
        self.assertEqual(salary.taxes, 0)
        self.assertEqual(salary.penalty, penalty.sum)
        self.assertEqual(salary.total, salary.sum - penalty.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 2)

    def test_with_opened_issues_mr(self):
        closed_issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)
        opened_issue = IssueFactory.create(state=ISSUE_STATES.OPENED)
        opened_mr = MergeRequestFactory.create(state=ISSUE_STATES.OPENED)

        IssueSpentTimeFactory.create(user=self.user, base=opened_issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=closed_issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=closed_issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        MergeRequestSpentTimeFactory.create(user=self.user, base=opened_mr,
                                            time_spent=timedelta(
                                                hours=5).total_seconds())

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=3))
        self.assertEqual(salary.sum, self.user.hour_rate * 3)
        self.assertEqual(salary.bonus, 0)
        self.assertEqual(salary.penalty, 0)
        self.assertEqual(salary.taxes, 0)
        self.assertEqual(salary.total, salary.sum)

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 2)

    def test_taxes(self):
        self.user.taxes = 0.3
        self.user.save()

        issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=-timedelta(
                                         hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue,
                                     time_spent=timedelta(
                                         hours=5).total_seconds())

        bonus = BonusFactory.create(user=self.user)
        penalty = PenaltyFactory.create(user=self.user, sum=100)

        salary = self.calculator.generate(self.user)

        self.assertEqual(salary.charged_time,
                         seconds(hours=4))
        self.assertEqual(salary.sum, self.user.hour_rate * 4)
        self.assertEqual(salary.bonus, bonus.sum)
        self.assertEqual(salary.penalty, penalty.sum)
        self.assertEqual(salary.total, salary.sum + bonus.sum - penalty.sum)
        self.assertEqual(salary.taxes,
                         salary.total * Decimal.from_float(self.user.taxes))

        self.assertEqual(Payroll.objects.filter(salary=salary).count(), 5)
