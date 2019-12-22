from apps.payroll.models import Payroll
from tests.test_payroll.factories import (
    BonusFactory,
    IssueSpentTimeFactory,
    PaymentFactory,
    PenaltyFactory,
)


def test_bonus(user, payroll_admin):
    bonus = BonusFactory.create(user=user)

    payroll = Payroll.objects.first()
    inheritance_link = payroll_admin.inheritance(payroll)
    expected = '<a href=/admin/payroll/bonus/{0}/change/>'.format(bonus.pk)

    assert expected in inheritance_link


def test_payment(user, payroll_admin):
    payment = PaymentFactory.create(user=user)

    payroll = Payroll.objects.first()
    inheritance_link = payroll_admin.inheritance(payroll)
    expected = '<a href=/admin/payroll/payment/{0}/change/>'.format(payment.pk)

    assert expected in inheritance_link


def test_penalty(user, payroll_admin):
    penalty = PenaltyFactory.create(user=user)

    payroll = Payroll.objects.first()
    inheritance_link = payroll_admin.inheritance(payroll)
    expected = '<a href=/admin/payroll/penalty/{0}/change/>'.format(penalty.pk)

    assert expected in inheritance_link


def test_spenttime(user, payroll_admin):
    spenttime = IssueSpentTimeFactory.create(user=user)

    payroll = Payroll.objects.first()
    inheritance_link = payroll_admin.inheritance(payroll)
    expected = '<a href=/admin/payroll/spenttime/{0}/change/>'.format(
        spenttime.pk,
    )

    assert expected in inheritance_link


def test_payroll(user, payroll_admin):
    payroll = Payroll.objects.create(user=user, created_by=user)
    assert payroll_admin.inheritance(payroll) is None
