from apps.payroll.models import Payroll


def test_str(user):
    payroll = Payroll.objects.create(created_by=user, user=user)

    assert str(payroll) == "{0} [{1}]: {2}".format(
        user,
        payroll.created_at,
        payroll.sum,
    )
