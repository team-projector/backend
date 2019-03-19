from datetime import timedelta

from django.test import TestCase

from apps.development.models import STATE_CLOSED, STATE_OPENED
from apps.development.tests.factories import IssueFactory
from apps.payroll.tests.factories import BonusFactory, IssueSpentTimeFactory, PenaltyFactory, SalaryFactory
from apps.payroll.utils.metrics.user import User, UserMetrics, UserMetricsCalculator
from apps.users.tests.factories import UserFactory


class UserMetricsTests(TestCase):
    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(login='user', hour_rate=100)

        self.calculator = UserMetricsCalculator()

    def test_issues_opened_count(self):
        IssueFactory.create_batch(10, user=self.user)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, issues_opened_count=10)

    def test_issues_opened_count_exists_closed(self):
        IssueFactory.create_batch(10, user=self.user)
        IssueFactory.create_batch(5, user=self.user, state=STATE_CLOSED)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, issues_opened_count=10)

    def test_issues_opened_count_another_user(self):
        user_2 = UserFactory.create()

        IssueFactory.create_batch(10, user=self.user)
        IssueFactory.create_batch(5, user=user_2)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, issues_opened_count=10)

    def test_bonus(self):
        bonuses = BonusFactory.create_batch(10, user=self.user)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))

    def test_bonus_have_salaries(self):
        bonuses = BonusFactory.create_batch(10, user=self.user)
        BonusFactory.create_batch(5, user=self.user, salary=SalaryFactory.create(user=self.user))

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))

    def test_bonus_another_user(self):
        bonuses = BonusFactory.create_batch(10, user=self.user)

        user_2 = UserFactory.create()
        BonusFactory.create_batch(5, user=user_2)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))

    def test_penalty(self):
        penalties = PenaltyFactory.create_batch(10, user=self.user)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))

    def test_penalty_have_salaries(self):
        penalties = PenaltyFactory.create_batch(10, user=self.user)
        PenaltyFactory.create_batch(5, user=self.user, salary=SalaryFactory.create(user=self.user))

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))

    def test_penalty_another_user(self):
        penalties = PenaltyFactory.create_batch(10, user=self.user)

        user_2 = UserFactory.create()
        PenaltyFactory.create_batch(5, user=user_2)

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))

    def test_payroll_opened(self):
        issue = IssueFactory.create(state=STATE_OPENED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, payroll_opened=self.user.hour_rate * 4)

    def test_payroll_opened_has_salary(self):
        issue = IssueFactory.create(state=STATE_OPENED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=4).total_seconds(),
                                     salary=SalaryFactory.create(user=self.user))
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, payroll_opened=self.user.hour_rate * 7)

    def test_payroll_opened_has_closed(self):
        issue = IssueFactory.create(state=STATE_CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=4).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=IssueFactory.create(),
                                     time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics,
                            payroll_opened=self.user.hour_rate * 5,
                            payroll_closed=self.user.hour_rate * 6)

    def test_payroll_opened_another_user(self):
        issue = IssueFactory.create(state=STATE_OPENED)

        user_2 = UserFactory.create()

        IssueSpentTimeFactory.create(user=user_2, base=issue, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=user_2, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, payroll_opened=self.user.hour_rate * 5)

    def test_payroll_closed(self):
        issue = IssueFactory.create(state=STATE_CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=-timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, payroll_closed=self.user.hour_rate * 4)

    def test_payroll_closed_has_salary(self):
        issue = IssueFactory.create(state=STATE_CLOSED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=4).total_seconds(),
                                     salary=SalaryFactory.create(user=self.user))
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, payroll_closed=self.user.hour_rate * 7)

    def test_payroll_opened_has_opened(self):
        issue = IssueFactory.create(state=STATE_OPENED)

        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=4).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=IssueFactory.create(state=STATE_CLOSED),
                                     time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics,
                            payroll_closed=self.user.hour_rate * 5,
                            payroll_opened=self.user.hour_rate * 6)

    def test_payroll_closed_another_user(self):
        issue = IssueFactory.create(state=STATE_CLOSED)

        user_2 = UserFactory.create()

        IssueSpentTimeFactory.create(user=user_2, base=issue, time_spent=timedelta(hours=1).total_seconds())
        IssueSpentTimeFactory.create(user=user_2, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics, payroll_closed=self.user.hour_rate * 5)

    def test_complex(self):
        bonuses = BonusFactory.create_batch(10, user=self.user)
        penalties = PenaltyFactory.create_batch(10, user=self.user)

        issue = IssueFactory.create(user=self.user, state=STATE_OPENED)
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=4).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=issue, time_spent=timedelta(hours=2).total_seconds())
        IssueSpentTimeFactory.create(user=self.user, base=IssueFactory.create(user=self.user, state=STATE_CLOSED),
                                     time_spent=timedelta(hours=5).total_seconds())

        metrics = self.calculator.calculate(self.user)

        self._check_metrics(metrics,
                            issues_opened_count=1,
                            bonus=sum(bonus.sum for bonus in bonuses),
                            penalty=sum(penalty.sum for penalty in penalties),
                            payroll_closed=self.user.hour_rate * 5,
                            payroll_opened=self.user.hour_rate * 6)

    def _check_metrics(self, metrics: UserMetrics,
                       issues_opened_count=0,
                       bonus=0,
                       penalty=0,
                       payroll_opened=0,
                       payroll_closed=0):
        self.assertEqual(metrics.bonus, bonus)
        self.assertEqual(metrics.penalty, penalty)
        self.assertEqual(metrics.issues_opened_count, issues_opened_count)
        self.assertEqual(metrics.payroll_opened, payroll_opened)
        self.assertEqual(metrics.payroll_closed, payroll_closed)
