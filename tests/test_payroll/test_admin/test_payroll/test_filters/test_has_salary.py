# -*- coding: utf-8 -*-

from apps.payroll.admin.filters import HasSalaryFilter
from apps.payroll.models import Payroll, Salary
from tests.test_payroll.factories import SalaryFactory


def test_true(user, admin_client, payroll_admin):
    payroll = Payroll.objects.create(
        created_by=user, user=user, salary=SalaryFactory.create(user=user),
    )

    has_salary_filter = HasSalaryFilter(
        request=admin_client.get("/admin/payroll/salary/"),
        params={"has_salary": True},
        model=Salary,
        model_admin=payroll_admin,
    )

    assert has_salary_filter.has_output() is True

    payroll_with_salaries = has_salary_filter.queryset(None, Payroll.objects)

    assert payroll_with_salaries.count() == 1
    assert payroll_with_salaries.first() == payroll


def test_false(user, admin_client, payroll_admin):
    payroll = Payroll.objects.create(created_by=user, user=user)

    has_salary_filter = HasSalaryFilter(
        request=admin_client.get("/admin/payroll/salary/"),
        params={"has_salary": False},
        model=Salary,
        model_admin=payroll_admin,
    )

    payroll_without_salaries = has_salary_filter.queryset(
        None, Payroll.objects,
    )

    assert payroll_without_salaries.count() == 1
    assert payroll_without_salaries.first() == payroll
