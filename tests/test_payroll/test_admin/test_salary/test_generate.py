# -*- coding: utf-8 -*-

from datetime import timedelta
from http import HTTPStatus

import pytest
from django.utils import timezone

from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.payroll.models import Salary
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


@pytest.fixture()
def issue():
    return IssueFactory.create(state=IssueState.CLOSED)


@pytest.fixture()
def issue_spent_time(user, issue):
    return IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=5)
    )


def test_get_form(admin_client, salary_admin):
    response = salary_admin.generate_salaries(
        admin_client.get("/admin/payroll/salary/")
    )

    assert response.status_code == HTTPStatus.OK
    assert Salary.objects.count() == 0
    assert b"/admin/payroll/salary/generate/" in response.content
    assert b"period_from" in response.content
    assert b"period_to" in response.content


def test_generate_salaries(issue_spent_time, admin_client, salary_admin):
    response = salary_admin.generate_salaries(
        admin_client.post("/admin/payroll/salary/", {
            "period_from": str(timezone.now().date() - timedelta(days=15)),
            "period_to": str(timezone.now().date())
        })
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Salary.objects.count() == 1

    salary = Salary.objects.first()
    assert salary.total == issue_spent_time.user.hour_rate * 5
    assert salary.period_from == timezone.now().date() - timedelta(days=15)
    assert salary.period_to == timezone.now().date()
