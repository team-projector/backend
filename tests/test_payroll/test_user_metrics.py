import pytest
from django.utils import timezone

from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.users.services.user import metrics
from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    BonusFactory,
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
    PenaltyFactory,
    SalaryFactory,
    WorkBreakFactory,
)
from tests.test_users.factories.user import UserFactory

calculator = UserMetricsProvider()


@pytest.fixture()
def user(db):
    yield UserFactory.create(
        login="user",
        hour_rate=100,
        tax_rate=15,
    )


def test_issues_opened_count(user):
    IssueFactory.create_batch(10, user=user)

    _check_metrics(calculator.get_metrics(user), issues_opened_count=10)


def test_mr_opened_count(user):
    MergeRequestFactory.create_batch(10, user=user)

    _check_metrics(calculator.get_metrics(user), mr_opened_count=10)


def test_issues_opened_count_exists_closed(user):
    IssueFactory.create_batch(10, user=user)
    IssueFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    _check_metrics(calculator.get_metrics(user), issues_opened_count=10)


def test_mr_opened_count_exists_closed(user):
    MergeRequestFactory.create_batch(10, user=user)
    MergeRequestFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    _check_metrics(calculator.get_metrics(user), mr_opened_count=10)


def test_issues_opened_count_another_user(user):
    user_2 = UserFactory.create()

    IssueFactory.create_batch(10, user=user)
    IssueFactory.create_batch(5, user=user_2)

    _check_metrics(calculator.get_metrics(user), issues_opened_count=10)


def test_mr_opened_count_another_user(user):
    user_2 = UserFactory.create()

    MergeRequestFactory.create_batch(10, user=user)
    MergeRequestFactory.create_batch(5, user=user_2)

    _check_metrics(calculator.get_metrics(user), mr_opened_count=10)


def test_bonus(user):
    bonuses = BonusFactory.create_batch(10, user=user)
    bonus_sum = metrics.bonus_resolver({"user": user}, None)
    assert bonus_sum == sum(bonus.sum for bonus in bonuses)


def test_bonus_have_salaries(user):
    bonuses = BonusFactory.create_batch(10, user=user)
    BonusFactory.create_batch(5, user=user,
                              salary=SalaryFactory.create(user=user))

    bonus_sum = metrics.bonus_resolver({"user": user}, None)
    assert bonus_sum == sum(bonus.sum for bonus in bonuses)


def test_bonus_another_user(user):
    bonuses = BonusFactory.create_batch(10, user=user)

    user_2 = UserFactory.create()
    BonusFactory.create_batch(5, user=user_2)

    bonus_sum = metrics.bonus_resolver({"user": user}, None)
    assert bonus_sum == sum(bonus.sum for bonus in bonuses)


def test_penalty(user):
    penalties = PenaltyFactory.create_batch(10, user=user)

    penalty_sum = metrics.penalty_resolver({"user": user}, None)
    assert penalty_sum == sum(penalty.sum for penalty in penalties)


def test_penalty_have_salaries(user):
    penalties = PenaltyFactory.create_batch(10, user=user)
    PenaltyFactory.create_batch(5, user=user,
                                salary=SalaryFactory.create(user=user))

    penalty_sum = metrics.penalty_resolver({"user": user}, None)
    assert penalty_sum == sum(penalty.sum for penalty in penalties)


def test_penalty_another_user(user):
    penalties = PenaltyFactory.create_batch(10, user=user)

    user_2 = UserFactory.create()
    PenaltyFactory.create_batch(5, user=user_2)

    penalty_sum = metrics.penalty_resolver({"user": user}, None)
    assert penalty_sum == sum(penalty.sum for penalty in penalties)


def test_payroll_opened(user):
    issue = IssueFactory.create(state=IssueState.OPENED)
    mr = MergeRequestFactory.create(
        state=MergeRequestState.OPENED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=1))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=-seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=5)
    )

    _check_metrics(
        calculator.get_metrics(user),
        payroll_opened=user.hour_rate * 9,
        taxes_opened=user.tax_rate * 9,
        issues_opened_spent=seconds(hours=4),
        mr_opened_spent=seconds(hours=5),
    )


def test_payroll_opened_has_salary(user):
    issue = IssueFactory.create(state=IssueState.OPENED)
    mr = MergeRequestFactory.create(
        state=MergeRequestState.OPENED)

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
        salary=salary,
    )

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=5)
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=2),
        salary=salary
    )

    _check_metrics(
        calculator.get_metrics(user),
        payroll_opened=user.hour_rate * 12,
        taxes_opened=user.tax_rate * 12,
        issues_opened_spent=seconds(hours=7),
        mr_opened_spent=seconds(hours=5),
    )


def test_payroll_opened_has_closed(user):
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, time_spent=seconds(hours=5))

    _check_metrics(
        calculator.get_metrics(user),
        payroll_opened=user.hour_rate * 5,
        taxes_opened=user.tax_rate * 5,
        issues_opened_spent=seconds(hours=5),
        payroll_closed=user.hour_rate * 6,
        taxes_closed=user.tax_rate * 6,
        issues_closed_spent=seconds(hours=6),
    )


def test_payroll_opened_another_user(user):
    issue = IssueFactory.create(state=IssueState.OPENED)

    user_2 = UserFactory.create()

    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=seconds(hours=1))
    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    _check_metrics(
        calculator.get_metrics(user),
        payroll_opened=user.hour_rate * 5,
        taxes_opened=user.tax_rate * 5,
        issues_opened_spent=seconds(hours=5),
    )


def test_payroll_closed(user):
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=1))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=-seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    _check_metrics(
        calculator.get_metrics(user),
        payroll_closed=user.hour_rate * 4,
        taxes_closed=user.tax_rate * 4,
        issues_closed_spent=seconds(hours=4),
    )


def test_payroll_closed_has_salary(user):
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4),
                                 salary=SalaryFactory.create(user=user))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    _check_metrics(
        calculator.get_metrics(user),
        payroll_closed=user.hour_rate * 7,
        taxes_closed=user.tax_rate * 7,
        issues_closed_spent=seconds(hours=7),
    )


def test_payroll_opened_has_opened(user):
    issue = IssueFactory.create(state=IssueState.OPENED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user,
                                 base=IssueFactory.create(
                                     state=IssueState.CLOSED),
                                 time_spent=seconds(hours=5))

    _check_metrics(
        calculator.get_metrics(user),
        payroll_closed=user.hour_rate * 5,
        taxes_closed=user.tax_rate * 5,
        issues_closed_spent=seconds(hours=5),
        payroll_opened=user.hour_rate * 6,
        taxes_opened=user.tax_rate * 6,
        issues_opened_spent=seconds(hours=6),
    )


def test_payroll_closed_another_user(user):
    issue = IssueFactory.create(state=IssueState.CLOSED)
    mr = MergeRequestFactory.create(state=IssueState.CLOSED)

    user_2 = UserFactory.create()

    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=seconds(hours=1))
    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=2),
    )

    _check_metrics(
        calculator.get_metrics(user),
        payroll_closed=user.hour_rate * 7,
        taxes_closed=user.tax_rate * 7,
        issues_closed_spent=seconds(hours=5),
        mr_closed_spent=seconds(hours=2),
    )


def test_last_salary_date(user):
    SalaryFactory(
        user=user,
        period_to=timezone.now() - timezone.timedelta(days=30),
        payed=True,
    )
    salary = SalaryFactory(
        user=user,
        period_to=timezone.now(),
        payed=True,
    )

    last_salary_date = metrics.last_salary_date_resolver({"user": user}, None)
    assert last_salary_date == salary.created_at


def test_last_salary_date_not_paid(user):
    SalaryFactory(user=user, payed=False)
    last_salary_date = metrics.last_salary_date_resolver({"user": user}, None)
    assert not last_salary_date


def test_paid_work_breaks_days(user):
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=now,
        from_date=now - timezone.timedelta(days=5),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        {"user": user},
        None,
    )
    assert paid_work_breaks_days == 5


def test_paid_work_breaks_days_not_paid_not_count(user):
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=False,
        to_date=now,
        from_date=now - timezone.timedelta(days=5),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        {"user": user},
        None,
    )
    assert paid_work_breaks_days == 0


def test_paid_work_breaks_days_not_this_year_not_count(user):
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=now - timezone.timedelta(days=370),
        from_date=now - timezone.timedelta(days=375),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        {"user": user},
        None,
    )
    assert paid_work_breaks_days == 0


def test_paid_work_breaks_lower_boundary_of_year(user):
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=timezone.make_aware(timezone.datetime(now.year, 1, 3)),
        from_date=timezone.make_aware(timezone.datetime(now.year - 1, 12, 25)),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        {"user": user},
        None,
    )
    assert paid_work_breaks_days == 3


def test_paid_work_breaks_upper_boundary_of_year(user):
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=timezone.make_aware(timezone.datetime(now.year + 1, 1, 3)),
        from_date=timezone.make_aware(timezone.datetime(now.year, 12, 25)),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        {"user": user},
        None,
    )
    assert paid_work_breaks_days == 7


def test_complex(user):
    BonusFactory.create_batch(10, user=user)
    PenaltyFactory.create_batch(10, user=user)

    issue = IssueFactory.create(user=user, state=IssueState.OPENED)
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(
            user=user,
            state=IssueState.CLOSED,
        ),
        time_spent=seconds(hours=5),
    )

    _check_metrics(
        calculator.get_metrics(user),
        issues_opened_count=1,
        payroll_closed=user.hour_rate * 5,
        taxes_closed=user.tax_rate * 5,
        issues_closed_spent=seconds(hours=5),
        payroll_opened=user.hour_rate * 6,
        taxes_opened=user.tax_rate * 6,
        issues_opened_spent=seconds(hours=6),
    )


def test_resolver(user, ghl_mock_info):
    IssueFactory.create_batch(10, user=user)

    _check_metrics(calculator.get_metrics(user), issues_opened_count=10)


def _check_metrics(
    metrics,
    payroll_opened=0,
    payroll_closed=0,
    taxes_opened=0,
    taxes_closed=0,
    issues_opened_count=0,
    issues_closed_spent=0.0,
    issues_opened_spent=0.0,
    mr_opened_count=0,
    mr_closed_spent=0.0,
    mr_opened_spent=0.0,
):
    assert payroll_opened == metrics["payroll_opened"]
    assert payroll_closed == metrics["payroll_closed"]
    assert payroll_opened + payroll_closed == metrics["payroll"]

    assert taxes_opened == metrics["taxes_opened"]
    assert taxes_closed == metrics["taxes_closed"]
    assert taxes_opened + taxes_closed == metrics["taxes"]

    assert issues_opened_count == metrics["issues"]["opened_count"]
    assert issues_closed_spent == metrics["issues"]["closed_spent"]
    assert issues_opened_spent == metrics["issues"]["opened_spent"]

    assert mr_opened_count == metrics["merge_requests"]["opened_count"]
    assert mr_closed_spent == metrics["merge_requests"]["closed_spent"]
    assert mr_opened_spent == metrics["merge_requests"]["opened_spent"]

    opened_spent = mr_opened_spent + issues_opened_spent
    closed_spent = mr_closed_spent + issues_closed_spent
    assert opened_spent == metrics["opened_spent"]
    assert closed_spent == metrics["closed_spent"]
