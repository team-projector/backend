import pytest
from django.contrib.auth import get_user_model

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.users.services import user as user_service
from apps.users.graphql.types.user import UserType
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    BonusFactory, IssueSpentTimeFactory, MergeRequestSpentTimeFactory,
    PenaltyFactory, SalaryFactory
)
from tests.test_users.factories.user import UserFactory

calculator = user_service.UserMetricsProvider()


@pytest.fixture
def user(db):
    yield get_user_model().objects.create_user(login='user', hour_rate=100)


def test_issues_opened_count(user):
    IssueFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, issues_opened_count=10)


def test_mr_opened_count(user):
    MergeRequestFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, mr_opened_count=10)


def test_issues_opened_count_exists_closed(user):
    IssueFactory.create_batch(10, user=user)
    IssueFactory.create_batch(5, user=user, state=ISSUE_STATES.CLOSED)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, issues_opened_count=10)


def test_mr_opened_count_exists_closed(user):
    MergeRequestFactory.create_batch(10, user=user)
    MergeRequestFactory.create_batch(5, user=user, state=ISSUE_STATES.CLOSED)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, mr_opened_count=10)


def test_issues_opened_count_another_user(user):
    user_2 = UserFactory.create()

    IssueFactory.create_batch(10, user=user)
    IssueFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, issues_opened_count=10)


def test_mr_opened_count_another_user(user):
    user_2 = UserFactory.create()

    MergeRequestFactory.create_batch(10, user=user)
    MergeRequestFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, mr_opened_count=10)


def test_bonus(user):
    bonuses = BonusFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))


def test_bonus_have_salaries(user):
    bonuses = BonusFactory.create_batch(10, user=user)
    BonusFactory.create_batch(5, user=user,
                              salary=SalaryFactory.create(user=user))

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))


def test_bonus_another_user(user):
    bonuses = BonusFactory.create_batch(10, user=user)

    user_2 = UserFactory.create()
    BonusFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, bonus=sum(bonus.sum for bonus in bonuses))


def test_penalty(user):
    penalties = PenaltyFactory.create_batch(10, user=user)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))


def test_penalty_have_salaries(user):
    penalties = PenaltyFactory.create_batch(10, user=user)
    PenaltyFactory.create_batch(5, user=user,
                                salary=SalaryFactory.create(user=user))

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))


def test_penalty_another_user(user):
    penalties = PenaltyFactory.create_batch(10, user=user)

    user_2 = UserFactory.create()
    PenaltyFactory.create_batch(5, user=user_2)

    metrics = calculator.get_metrics(user)

    _check_metrics(metrics, penalty=sum(penalty.sum for penalty in penalties))


def test_payroll_opened(user):
    issue = IssueFactory.create(state=ISSUE_STATES.OPENED)
    mr = MergeRequestFactory.create(state=user_service.MERGE_REQUESTS_STATES.OPENED)

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

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 9,
        issues_opened_spent=seconds(hours=4),
        mr_opened_spent=seconds(hours=5)
    )


def test_payroll_opened_has_salary(user):
    issue = IssueFactory.create(state=ISSUE_STATES.OPENED)
    mr = MergeRequestFactory.create(state=user_service.MERGE_REQUESTS_STATES.OPENED)

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
        salary=salary
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

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 12,
        issues_opened_spent=seconds(hours=7),
        mr_opened_spent=seconds(hours=5),
    )


def test_payroll_opened_has_closed(user):
    issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, time_spent=seconds(hours=5))

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 5,
        issues_opened_spent=seconds(hours=5),
        payroll_closed=user.hour_rate * 6,
        issues_closed_spent=seconds(hours=6)
    )


def test_payroll_opened_another_user(user):
    issue = IssueFactory.create(state=ISSUE_STATES.OPENED)

    user_2 = UserFactory.create()

    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=seconds(hours=1))
    IssueSpentTimeFactory.create(user=user_2, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_opened=user.hour_rate * 5,
        issues_opened_spent=seconds(hours=5)
    )


def test_payroll_closed(user):
    issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=1))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=-seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 4,
        issues_closed_spent=seconds(hours=4)
    )


def test_payroll_closed_has_salary(user):
    issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4),
                                 salary=SalaryFactory.create(user=user))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=5))

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 7,
        issues_closed_spent=seconds(hours=7)
    )


def test_payroll_opened_has_opened(user):
    issue = IssueFactory.create(state=ISSUE_STATES.OPENED)

    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user,
                                 base=IssueFactory.create(state=ISSUE_STATES.CLOSED),
                                 time_spent=seconds(hours=5))

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 5,
        issues_closed_spent=seconds(hours=5),
        payroll_opened=user.hour_rate * 6,
        issues_opened_spent=seconds(hours=6)
    )


def test_payroll_closed_another_user(user):
    issue = IssueFactory.create(state=ISSUE_STATES.CLOSED)
    mr = MergeRequestFactory.create(state=ISSUE_STATES.CLOSED)

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
        time_spent=seconds(hours=2)
    )

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        payroll_closed=user.hour_rate * 7,
        issues_closed_spent=seconds(hours=5),
        mr_closed_spent=seconds(hours=2),
    )


def test_complex(user):
    bonuses = BonusFactory.create_batch(10, user=user)
    penalties = PenaltyFactory.create_batch(10, user=user)

    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=4))
    IssueSpentTimeFactory.create(user=user, base=issue,
                                 time_spent=seconds(hours=2))
    IssueSpentTimeFactory.create(user=user,
                                 base=IssueFactory.create(user=user,
                                                          state=ISSUE_STATES.CLOSED),
                                 time_spent=seconds(hours=5))

    metrics = calculator.get_metrics(user)

    _check_metrics(
        metrics,
        issues_opened_count=1,
        bonus=sum(bonus.sum for bonus in bonuses),
        penalty=sum(penalty.sum for penalty in penalties),
        payroll_closed=user.hour_rate * 5,
        issues_closed_spent=seconds(hours=5),
        payroll_opened=user.hour_rate * 6,
        issues_opened_spent=seconds(hours=6)
    )


def test_resolver(user):
    IssueFactory.create_batch(10, user=user)

    metrics = UserType.resolve_metrics(user, None)

    _check_metrics(metrics, issues_opened_count=10)


def _check_metrics(metrics: user_service.UserMetrics,
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
