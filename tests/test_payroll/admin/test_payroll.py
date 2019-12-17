from apps.payroll.admin.filters import HasSalaryFilter
from apps.payroll.models import Payroll, Salary
from tests.helpers.base import model_admin
from tests.test_payroll.factories import (
    BonusFactory,
    IssueSpentTimeFactory,
    PaymentFactory,
    PenaltyFactory,
    SalaryFactory,
)
from tests.test_users.factories.user import UserFactory


def test_payroll_instance_str(db):
    user = UserFactory.create()
    payroll = Payroll.objects.create(created_by=user, user=user)

    assert str(payroll) == '{0} [{1}]: {2}'.format(
        user,
        payroll.created_at,
        payroll.sum,
    )


def test_inheritance_bonus(db):
    ma_payroll = model_admin(Payroll)

    bonus = BonusFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert f'<a href=/admin/payroll/bonus/{bonus.id}/change/>' in inheritance


def test_inheritance_payment(db):
    ma_payroll = model_admin(Payroll)

    payment = PaymentFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert (
        f'<a href=/admin/payroll/payment/{payment.id}/change/>' in inheritance
    )


def test_inheritance_penalty(db):
    ma_payroll = model_admin(Payroll)

    penalty = PenaltyFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert (
        f'<a href=/admin/payroll/penalty/{penalty.id}/change/>' in inheritance
    )


def test_inheritance_spenttime(db):
    ma_payroll = model_admin(Payroll)

    spenttime = IssueSpentTimeFactory.create(user=UserFactory.create())

    payroll = Payroll.objects.first()
    inheritance = ma_payroll.inheritance(payroll)

    assert (
        f'<a href=/admin/payroll/spenttime/{spenttime.id}/change/>'
        in inheritance
    )


def test_inheritance_payroll(db):
    ma_payroll = model_admin(Payroll)

    user = UserFactory.create()
    payroll = Payroll.objects.create(user=user,
                                     created_by=user)

    assert ma_payroll.inheritance(payroll) is None


def test_salary_filter_has_salary(admin_client):
    ma_salary = model_admin(Salary)

    user = UserFactory.create()

    payroll_1 = Payroll.objects.create(created_by=user, user=user)
    payroll_2 = Payroll.objects.create(
        created_by=user,
        user=user,
        salary=SalaryFactory.create(user=user),
    )

    has_salary_filter = HasSalaryFilter(
        request=admin_client.get('/admin/payroll/salary/'),
        params={'has_salary': True},
        model=Salary,
        model_admin=ma_salary
    )

    assert has_salary_filter.has_output() is True

    payroll_with_salaries = has_salary_filter.queryset(None, Payroll.objects)

    assert payroll_with_salaries.count() == 1
    assert payroll_with_salaries.first() == payroll_2

    has_salary_filter = HasSalaryFilter(
        request=admin_client.get('/admin/payroll/salary/'),
        params={'has_salary': False},
        model=Salary,
        model_admin=ma_salary
    )

    payroll_without_salaries = has_salary_filter.queryset(None, Payroll.objects)

    assert payroll_without_salaries.count() == 1
    assert payroll_without_salaries.first() == payroll_1

    has_salary_filter = HasSalaryFilter(
        request=admin_client.get('/admin/payroll/salary/'),
        params={},
        model=Salary,
        model_admin=ma_salary
    )

    payroll_all = has_salary_filter.queryset(None, Payroll.objects)

    assert payroll_all.count() == 2
