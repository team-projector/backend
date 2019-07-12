import pytest

from django.contrib.admin import site

from apps.payroll.models import Payroll
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, BonusFactory, PaymentFactory, PenaltyFactory
)
from tests.test_users.factories import UserFactory


@pytest.fixture
def model_admin(db):
    yield site._registry[Payroll]


def test_payroll_instance_str(db):
    user = UserFactory.create()
    payroll = Payroll.objects.create(created_by=user, user=user)

    assert str(payroll) == f'{user} [{payroll.created_at}]: {payroll.sum}'


def test_inheritance_bonus(model_admin):
    bonus = BonusFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = model_admin.inheritance(payroll)

    assert f'<a href=/admin/payroll/bonus/{bonus.id}/change/>' \
           in inheritance


def test_inheritance_payment(model_admin):
    payment = PaymentFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = model_admin.inheritance(payroll)

    assert f'<a href=/admin/payroll/payment/{payment.id}/change/>' \
           in inheritance


def test_inheritance_penalty(model_admin):
    penalty = PenaltyFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = model_admin.inheritance(payroll)

    assert f'<a href=/admin/payroll/penalty/{penalty.id}/change/>' \
           in inheritance


def test_inheritance_spenttime(model_admin):
    spenttime = IssueSpentTimeFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = model_admin.inheritance(payroll)

    assert f'<a href=/admin/payroll/spenttime/{spenttime.id}/change/>' \
           in inheritance
