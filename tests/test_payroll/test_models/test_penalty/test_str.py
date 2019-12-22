from tests.test_payroll.factories import PenaltyFactory


def test_str(user):
    penalty = PenaltyFactory.create(user=user, sum=150)

    assert str(penalty) == '{0} [{1}]: 150'.format(
        user.login,
        penalty.created_at,
    )
