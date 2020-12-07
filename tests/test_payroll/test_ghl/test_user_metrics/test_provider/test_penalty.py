from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_payroll.factories import PenaltyFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory

calculator = UserMetricsProvider


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
        5,
        user=user,
        salary=SalaryFactory.create(user=user),
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
