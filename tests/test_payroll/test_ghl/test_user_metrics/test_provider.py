# -*- coding: utf-8 -*-

import pytest
from django.utils import timezone
from jnt_django_toolbox.helpers.time import seconds

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

calculator = UserMetricsProvider


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    yield UserFactory.create(
        login="user", hour_rate=100, tax_rate=15,
    )


def test_issues_opened_count(user, ghl_auth_mock_info):
    """
    Test issues opened count.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(5, user=user)

    expected = metrics.issues_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 5


def test_mr_opened_count(user, ghl_auth_mock_info):
    """
    Test mr opened count.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(5, user=user)

    expected = metrics.mr_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 5


def test_issues_opened_count_exists_closed(user, ghl_auth_mock_info):
    """
    Test issues opened count exists closed.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(5, user=user)
    IssueFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    expected = metrics.issues_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 5


def test_mr_opened_count_exists_closed(user, ghl_auth_mock_info):
    """
    Test mr opened count exists closed.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(5, user=user, state=IssueState.CLOSED)

    expected = metrics.mr_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 2


def test_issues_opened_count_another_user(user, ghl_auth_mock_info):
    """
    Test issues opened count another user.

    :param user:
    :param ghl_auth_mock_info:
    """
    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(5, user=UserFactory.create())

    expected = metrics.issues_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 2


def test_mr_opened_count_another_user(user, ghl_auth_mock_info):
    """
    Test mr opened count another user.

    :param user:
    :param ghl_auth_mock_info:
    """
    MergeRequestFactory.create_batch(2, user=user)
    MergeRequestFactory.create_batch(5, user=UserFactory.create())

    expected = metrics.mr_opened_count_resolver(None, ghl_auth_mock_info)
    assert expected == 2


def test_payroll_opened(user):
    """
    Test payroll opened.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)
    mr = MergeRequestFactory.create(state=MergeRequestState.OPENED)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=-seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr, time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics,
        issues_opened_spent=seconds(hours=4),
        mr_opened_spent=seconds(hours=5),
    )
    _check_taxes(
        metrics,
        taxes_opened=user.hour_rate * 9 * user.tax_rate,
        taxes=user.hour_rate * 9 * user.tax_rate,
    )
    _check_payroll(
        metrics, payroll_opened=user.hour_rate * 9,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_opened=user.hour_rate * 4 * user.tax_rate,
        taxes=user.hour_rate * 4 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"], payroll_opened=user.hour_rate * 4,
    )

    # check merge_request
    _check_taxes(
        metrics["merge_requests"],
        taxes_opened=user.hour_rate * 5 * user.tax_rate,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    _check_payroll(
        metrics["merge_requests"], payroll_opened=user.hour_rate * 5,
    )


def test_payroll_opened_has_salary(user):
    """
    Test payroll opened has salary.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)
    mr = MergeRequestFactory.create(state=MergeRequestState.OPENED)

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=4), salary=salary,
    )

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr, time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr, time_spent=seconds(hours=2), salary=salary,
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics,
        mr_opened_spent=seconds(hours=5),
        issues_opened_spent=seconds(hours=7),
    )
    _check_taxes(
        metrics,
        taxes_opened=user.tax_rate * user.hour_rate * 12,
        taxes=user.hour_rate * 12 * user.tax_rate,
    )
    _check_payroll(
        metrics, payroll_opened=user.hour_rate * 12,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_opened=user.hour_rate * 7 * user.tax_rate,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"], payroll_opened=user.hour_rate * 7,
    )

    # check merge_request
    _check_taxes(
        metrics["merge_requests"],
        taxes_opened=user.hour_rate * 5 * user.tax_rate,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    _check_payroll(
        metrics["merge_requests"], payroll_opened=user.hour_rate * 5,
    )


def test_payroll_opened_has_closed(user):
    """
    Test payroll opened has closed.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(user=user, time_spent=seconds(hours=5))

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics,
        issues_closed_spent=seconds(hours=6),
        issues_opened_spent=seconds(hours=5),
    )
    _check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 6,
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    _check_payroll(
        metrics,
        payroll_opened=user.hour_rate * 5,
        payroll_closed=user.hour_rate * 6,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 6,
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"],
        payroll_opened=user.hour_rate * 5,
        payroll_closed=user.hour_rate * 6,
    )

    # check merge_request
    _check_taxes(metrics["merge_requests"])
    _check_payroll(metrics["merge_requests"])


def test_payroll_opened_another_user(user):
    """
    Test payroll opened another user.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        user=another_user, base=issue, time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=another_user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics, issues_opened_spent=seconds(hours=5),
    )
    _check_taxes(
        metrics,
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    _check_payroll(
        metrics, payroll_opened=user.hour_rate * 5,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"], payroll_opened=user.hour_rate * 5,
    )

    # check merge_request
    _check_taxes(metrics["merge_requests"])
    _check_payroll(metrics["merge_requests"])


def test_payroll_closed(user):
    """
    Test payroll closed.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=-seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics, issues_closed_spent=seconds(hours=4),
    )
    _check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 4,
        taxes=user.hour_rate * 4 * user.tax_rate,
    )
    _check_payroll(
        metrics, payroll_closed=user.hour_rate * 4,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 4,
        taxes=user.hour_rate * 4 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"], payroll_closed=user.hour_rate * 4,
    )

    # check merge_request
    _check_taxes(metrics["merge_requests"])
    _check_payroll(metrics["merge_requests"])


def test_payroll_closed_has_salary(user):
    """
    Test payroll closed has salary.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
        salary=SalaryFactory.create(user=user),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics, issues_closed_spent=seconds(hours=7),
    )
    _check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 7,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    _check_payroll(
        metrics, payroll_closed=user.hour_rate * 7,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 7,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"], payroll_closed=user.hour_rate * 7,
    )

    # check merge_request
    _check_taxes(metrics["merge_requests"])
    _check_payroll(metrics["merge_requests"])


def test_payroll_opened_has_opened(user):
    """
    Test payroll opened has opened.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)

    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(state=IssueState.CLOSED),
        time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics,
        issues_closed_spent=seconds(hours=5),
        issues_opened_spent=seconds(hours=6),
    )
    _check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    _check_payroll(
        metrics,
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    _check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )

    # check merge_request
    _check_taxes(metrics["merge_requests"])
    _check_payroll(metrics["merge_requests"])


def test_payroll_closed_another_user(user):
    """
    Test payroll closed another user.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)
    mr = MergeRequestFactory.create(state=IssueState.CLOSED)

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        user=another_user, base=issue, time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=another_user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=mr, time_spent=seconds(hours=2),
    )

    metrics = calculator().get_metrics(user)

    # check common
    _check_spent(
        metrics,
        issues_closed_spent=seconds(hours=5),
        mr_closed_spent=seconds(hours=2),
    )
    _check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 7,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    _check_payroll(metrics, payroll_closed=user.hour_rate * 7)

    # check issues
    _check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    _check_payroll(metrics["issues"], payroll_closed=user.hour_rate * 5)

    # check merge_request
    _check_taxes(
        metrics["merge_requests"],
        taxes_closed=user.tax_rate * user.hour_rate * 2,
        taxes=user.hour_rate * 2 * user.tax_rate,
    )
    _check_payroll(
        metrics["merge_requests"], payroll_closed=user.hour_rate * 2,
    )


def test_last_salary_date(user, ghl_auth_mock_info):
    """
    Test last salary date.

    :param user:
    :param ghl_auth_mock_info:
    """
    SalaryFactory(
        user=user,
        period_to=timezone.now() - timezone.timedelta(days=30),
        payed=True,
    )
    salary = SalaryFactory(user=user, period_to=timezone.now())

    last_salary_date = metrics.last_salary_date_resolver(
        None, ghl_auth_mock_info,
    )
    assert last_salary_date == salary.period_to.date()


def test_bonus(user):
    """
    Test bonus.

    :param user:
    """
    bonuses = BonusFactory.create_batch(10, user=user)

    metrics = calculator().get_metrics(user)

    bonus = sum(bonus.sum for bonus in bonuses)
    assert metrics["bonus"] == bonus
    _check_taxes(metrics, taxes=bonus * user.tax_rate)


def test_bonus_have_salaries(user):
    """
    Test bonus have salaries.

    :param user:
    """
    bonuses = BonusFactory.create_batch(10, user=user)
    BonusFactory.create_batch(
        5, user=user, salary=SalaryFactory.create(user=user),
    )

    metrics = calculator().get_metrics(user)

    bonus = sum(bonus.sum for bonus in bonuses)
    assert metrics["bonus"] == bonus
    _check_taxes(metrics, taxes=bonus * user.tax_rate)


def test_bonus_another_user(user):
    """
    Test bonus another user.

    :param user:
    """
    bonuses = BonusFactory.create_batch(10, user=user)

    BonusFactory.create_batch(5, user=UserFactory.create())

    metrics = calculator().get_metrics(user)

    bonus = sum(bonus.sum for bonus in bonuses)
    assert metrics["bonus"] == bonus
    _check_taxes(metrics, taxes=bonus * user.tax_rate)


def test_penalty(user):
    """
    Test penalty.

    :param user:
    """
    penalties = PenaltyFactory.create_batch(10, user=user)

    metrics = calculator().get_metrics(user)

    penalty = sum(penalty.sum for penalty in penalties)
    assert metrics["penalty"] == penalty


def test_penalty_have_salaries(user):
    """
    Test penalty have salaries.

    :param user:
    """
    penalties = PenaltyFactory.create_batch(10, user=user)
    PenaltyFactory.create_batch(
        5, user=user, salary=SalaryFactory.create(user=user),
    )

    metrics = calculator().get_metrics(user)

    penalty = sum(penalty.sum for penalty in penalties)
    assert metrics["penalty"] == penalty


def test_penalty_another_user(user):
    """
    Test penalty another user.

    :param user:
    """
    penalties = PenaltyFactory.create_batch(10, user=user)

    PenaltyFactory.create_batch(5, user=UserFactory.create())

    metrics = calculator().get_metrics(user)
    penalty = sum(penalty.sum for penalty in penalties)

    assert metrics["penalty"] == penalty


def test_paid_work_breaks_days(user, ghl_auth_mock_info):
    """
    Test paid work breaks days.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=now,
        from_date=now - timezone.timedelta(days=5),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        None, ghl_auth_mock_info,
    )
    assert paid_work_breaks_days == 5


def test_paid_work_breaks_days_not_paid_not_count(user, ghl_auth_mock_info):
    """
    Test paid work breaks days not paid not count.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=False,
        to_date=now,
        from_date=now - timezone.timedelta(days=5),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        None, ghl_auth_mock_info,
    )
    assert paid_work_breaks_days == 0


def test_paid_work_breaks_days_not_this_year(
    user, ghl_auth_mock_info,
):
    """
    Test paid work breaks days not this year.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=now - timezone.timedelta(days=370),
        from_date=now - timezone.timedelta(days=375),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        None, ghl_auth_mock_info,
    )
    assert paid_work_breaks_days == 0


def test_paid_work_breaks_lower_boundary_of_year(user, ghl_auth_mock_info):
    """
    Test paid work breaks lower boundary of year.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=timezone.make_aware(timezone.datetime(now.year, 1, 3)),
        from_date=timezone.make_aware(timezone.datetime(now.year - 1, 12, 25)),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        None, ghl_auth_mock_info,
    )
    assert paid_work_breaks_days == 3


def test_paid_work_breaks_upper_boundary_of_year(user, ghl_auth_mock_info):
    """
    Test paid work breaks upper boundary of year.

    :param user:
    :param ghl_auth_mock_info:
    """
    now = timezone.now()
    WorkBreakFactory(
        user=user,
        paid=True,
        to_date=timezone.make_aware(timezone.datetime(now.year + 1, 1, 3)),
        from_date=timezone.make_aware(timezone.datetime(now.year, 12, 25)),
    )
    paid_work_breaks_days = metrics.paid_work_breaks_days_resolver(
        None, ghl_auth_mock_info,
    )
    assert paid_work_breaks_days == 7


def test_complex(user):
    """
    Test complex.

    :param user:
    """
    BonusFactory.create_batch(10, sum=100, user=user)
    PenaltyFactory.create_batch(10, sum=50, user=user)

    issue = IssueFactory.create(user=user, state=IssueState.OPENED)
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user, base=issue, time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=IssueState.CLOSED),
        time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    bonus, penalty = 100 * 10, 50 * 10
    assert metrics["bonus"] == bonus
    assert metrics["penalty"] == penalty

    _check_spent(
        metrics,
        issues_closed_spent=seconds(hours=5),
        issues_opened_spent=seconds(hours=6),
    )
    _check_payroll(
        metrics,
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )
    _check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=(user.hour_rate * 11 + bonus - penalty) * user.tax_rate,
    )

    # check issues
    _check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )
    _check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )

    # check merge_request
    _check_taxes(metrics["merge_requests"])
    _check_payroll(metrics["merge_requests"])


def _check_payroll(
    metrics, payroll_opened=0, payroll_closed=0,
):
    """
    Check payroll.

    :param metrics:
    :param payroll_opened:
    :param payroll_closed:
    """
    assert payroll_opened == metrics["payroll_opened"]
    assert payroll_closed == metrics["payroll_closed"]
    assert payroll_opened + payroll_closed == metrics["payroll"]


def _check_taxes(
    metrics, taxes_opened=0, taxes_closed=0, taxes=0,
):
    """
    Check taxes.

    :param metrics:
    :param taxes_opened:
    :param taxes_closed:
    :param taxes:
    """
    assert taxes_opened == metrics["taxes_opened"]
    assert taxes_closed == metrics["taxes_closed"]
    assert taxes == metrics["taxes"]


def _check_spent(
    metrics,
    issues_closed_spent=0.0,
    issues_opened_spent=0.0,
    mr_closed_spent=0.0,
    mr_opened_spent=0.0,
):
    """
    Check spent.

    :param metrics:
    :param issues_closed_spent:
    :param issues_opened_spent:
    :param mr_closed_spent:
    :param mr_opened_spent:
    """
    assert issues_closed_spent == metrics["issues"]["closed_spent"]
    assert issues_opened_spent == metrics["issues"]["opened_spent"]

    assert mr_closed_spent == metrics["merge_requests"]["closed_spent"]
    assert mr_opened_spent == metrics["merge_requests"]["opened_spent"]

    opened_spent = mr_opened_spent + issues_opened_spent
    closed_spent = mr_closed_spent + issues_closed_spent
    assert opened_spent == metrics["opened_spent"]
    assert closed_spent == metrics["closed_spent"]
