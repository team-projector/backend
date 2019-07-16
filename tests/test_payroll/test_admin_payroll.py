from apps.payroll.models import Payroll
from tests.base import model_admin
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, BonusFactory, PaymentFactory, PenaltyFactory
)
from tests.test_users.factories import UserFactory


def test_payroll_instance_str(db):
    user = UserFactory.create()
    payroll = Payroll.objects.create(created_by=user, user=user)

    assert str(payroll) == f'{user} [{payroll.created_at}]: {payroll.sum}'


def test_inheritance_bonus(db):
    ma_payroll = model_admin(Payroll)

    bonus = BonusFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert f'<a href=/admin/payroll/bonus/{bonus.id}/change/>' \
           in inheritance


def test_inheritance_payment(db):
    ma_payroll = model_admin(Payroll)

    payment = PaymentFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert f'<a href=/admin/payroll/payment/{payment.id}/change/>' \
           in inheritance


def test_inheritance_penalty(db):
    ma_payroll = model_admin(Payroll)

    penalty = PenaltyFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert f'<a href=/admin/payroll/penalty/{penalty.id}/change/>' \
           in inheritance


def test_inheritance_spenttime(db):
    ma_payroll = model_admin(Payroll)

    spenttime = IssueSpentTimeFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert f'<a href=/admin/payroll/spenttime/{spenttime.id}/change/>' \
           in inheritance
