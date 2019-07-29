from datetime import timedelta

from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
from apps.payroll.services.metrics.user import (
    User, UserMetrics, UserMetricsProvider
)
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    BonusFactory, IssueSpentTimeFactory, PenaltyFactory, SalaryFactory,
    MergeRequestSpentTimeFactory)
from tests.test_users.factories import UserFactory

calculator = UserMetricsProvider()


def test_issues_opened_count(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    IssueFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, issues_opened_count=10)


def test_mr_opened_count(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    MergeRequestFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, mr_opened_count=10)


def test_issues_opened_count_exists_closed(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    IssueFactory.create_batch(10, user=user)
    IssueFactory.create_batch(5, user=user, state=STATE_CLOSED)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, issues_opened_count=10)


def test_mr_opened_count_exists_closed(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    MergeRequestFactory.create_batch(10, user=user)
    MergeRequestFactory.create_batch(5, user=user, state=STATE_CLOSED)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, mr_opened_count=10)


def test_issues_opened_count_another_user(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    user_2 = UserFactory.create()

    IssueFactory.create_batch(10, user=user)
    IssueFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, issues_opened_count=10)


def test_mr_opened_count_another_user(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    user_2 = UserFactory.create()

    MergeRequestFactory.create_batch(10, user=user)
    MergeRequestFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, mr_opened_count=10)


def test_bonus(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    bonuses = BonusFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))


def test_bonus_have_salaries(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    bonuses = BonusFactory.create_batch(10, user=user)
    BonusFactory.create_batch(5, user=user,
                              salary=SalaryFactory.create(user=user))

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))


def test_bonus_another_user(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    bonuses = BonusFactory.create_batch(10, user=user)

    user_2 = UserFactory.create()
    BonusFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))


def test_penalty(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    penalties = PenaltyFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))


def test_penalty_have_salaries(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    penalties = PenaltyFactory.create_batch(10, user=user)
    PenaltyFactory.create_batch(5, user=user,
                                salary=SalaryFactory.create(user=user))

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))


def test_penalty_another_user(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    penalties = PenaltyFactory.create_batch(10, user=user)

    user_2 = UserFactory.create()
    PenaltyFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))


def test_payroll_opened(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_OPENED)
    mr = MergeRequestFactory.create(state=STATE_OPENED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=1).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=-timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=timedelta(hours=5).total_seconds()
    )

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 9,
        issues_opened_spent=timedelta(hours=4).total_seconds(),
        mr_opened_spent=timedelta(hours=5).total_seconds()
    )


def test_payroll_opened_has_salary(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_OPENED)
    mr = MergeRequestFactory.create(state=STATE_OPENED)

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=4).total_seconds(),
        salary=salary
    )

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=timedelta(hours=5).total_seconds()
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=timedelta(hours=2).total_seconds(),
        salary=salary
    )

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 12,
        issues_opened_spent=timedelta(hours=7).total_seconds(),
        mr_opened_spent=timedelta(hours=5).total_seconds(),
    )


def test_payroll_opened_has_closed(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=4).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=IssueFactory.create(),
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 5,
        issues_opened_spent=timedelta(hours=5).total_seconds(),
        payroll_closed=user.hour_rate * 6,
        issues_closed_spent=timedelta(hours=6).total_seconds()
    )


def test_payroll_opened_another_user(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_OPENED)

    user_2 = UserFactory.create()

    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=timedelta(
                                     hours=1).total_seconds())
    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 5,
        issues_opened_spent=timedelta(hours=5).total_seconds()
    )


def test_payroll_closed(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=1).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=-timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 4,
        issues_closed_spent=timedelta(hours=4).total_seconds()
    )


def test_payroll_closed_has_salary(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=4).total_seconds(),
                                 salary=SalaryFactory.create(
                                     user=user))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 7,
        issues_closed_spent=timedelta(hours=7).total_seconds()
    )


def test_payroll_opened_has_opened(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_OPENED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=4).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=IssueFactory.create(
        state=STATE_CLOSED),
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 5,
        issues_closed_spent=timedelta(hours=5).total_seconds(),
        payroll_opened=user.hour_rate * 6,
        issues_opened_spent=timedelta(hours=6).total_seconds()
    )


def test_payroll_closed_another_user(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    issue = IssueFactory.create(state=STATE_CLOSED)
    mr = MergeRequestFactory.create(state=STATE_CLOSED)

    user_2 = UserFactory.create()

    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=timedelta(
                                     hours=1).total_seconds())
    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=timedelta(hours=2).total_seconds()
    )

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 7,
        issues_closed_spent=timedelta(hours=5).total_seconds(),
        mr_closed_spent=timedelta(hours=2).total_seconds(),
    )


def test_complex(db):
    user = User.objects.create_user(login='user', hour_rate=100)
    bonuses = BonusFactory.create_batch(10, user=user)
    penalties = PenaltyFactory.create_batch(10, user=user)

    issue = IssueFactory.create(user=user, state=STATE_OPENED)
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=4).total_seconds())
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=timedelta(
                                     hours=2).total_seconds())
    IssueSpentTimeFactory.create(user=user,
                                 base=IssueFactory.create(user=user,
                                                          state=STATE_CLOSED),
                                 time_spent=timedelta(
                                     hours=5).total_seconds())

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        issues_opened_count=1,
        bonus=sum(bonus.sum for bonus in bonuses),
        penalty=sum(penalty.sum for penalty in penalties),
        payroll_closed=user.hour_rate * 5,
        issues_closed_spent=timedelta(hours=5).total_seconds(),
        payroll_opened=user.hour_rate * 6,
        issues_opened_spent=timedelta(hours=6).total_seconds()
    )


def _check_metrics(metrics: UserMetrics,
                   bonus=0,
                   penalty=0,
                   payroll_opened=0,
                   payroll_closed=0,
                   issues_opened_count=0,
                   issues_closed_spent=0.0,
                   issues_opened_spent=0.0,
                   mr_opened_count=0,
                   mr_closed_spent=0.0,
                   mr_opened_spent=0.0):
    assert bonus == metrics.bonus
    assert penalty == metrics.penalty
    assert payroll_opened == metrics.payroll_opened
    assert payroll_closed == metrics.payroll_closed

    assert issues_opened_count == metrics.issues.opened_count
    assert issues_closed_spent == metrics.issues.closed_spent
    assert issues_opened_spent == metrics.issues.opened_spent

    assert mr_opened_count == metrics.merge_requests.opened_count
    assert mr_closed_spent == metrics.merge_requests.closed_spent
    assert mr_opened_spent == metrics.merge_requests.opened_spent
