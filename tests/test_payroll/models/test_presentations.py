from apps.payroll.models.work_break import WORK_BREAK_REASONS

from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import (
  BonusFactory,
  PaymentFactory,
  PenaltyFactory,
  SalaryFactory,
  IssueSpentTimeFactory,
  WorkBreakFactory,
)
from tests.test_users.factories import UserFactory


def test_bonus(db):
  user = UserFactory.create(login='login_test')
  bonus = BonusFactory.create(user=user, sum=150)

  assert str(bonus) == f'login_test [{bonus.created_at}]: 150'


def test_payment(db):
  user = UserFactory.create(login='login_test')
  payment = PaymentFactory.create(user=user, sum=150)

  assert str(payment) == f'login_test [{payment.created_at}]: 150'


def test_penalty(db):
  user = UserFactory.create(login='login_test')
  penalty = PenaltyFactory.create(user=user, sum=150)

  assert str(penalty) == f'login_test [{penalty.created_at}]: 150'


def test_salary(db):
  user = UserFactory.create(login='login_test')
  salary = SalaryFactory.create(user=user, sum=150)

  assert str(salary) == f'login_test [{salary.created_at}]: 150'


def test_spent_time(db):
  user = UserFactory.create(login='login_test')
  issue = IssueFactory.create(title='issue_title_test')
  spent_time = IssueSpentTimeFactory.create(user=user, time_spent=150, base=issue)

  assert str(spent_time) == 'login_test [issue_title_test]: 150'


def test_work_break(db):
  user = UserFactory.create(login='login_test')
  work_break = WorkBreakFactory.create(reason=WORK_BREAK_REASONS.dayoff, user=user)

  assert str(work_break) == f'login_test: {WORK_BREAK_REASONS.dayoff} ' \
                            f'({work_break.from_date} - {work_break.to_date})'
