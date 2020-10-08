from tests.test_payroll.factories import PaymentFactory


def test_str(user):
    """
    Test str.

    :param user:
    """
    payment = PaymentFactory.create(user=user, sum=150)

    assert str(payment) == "{0} [{1}]: 150".format(
        user.login,
        payment.created_at,
    )
