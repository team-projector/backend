from datetime import timedelta
import pytest

from rest_framework import status
from django.conf import settings
from django.contrib.admin import site
from django.core import mail
from django.utils import timezone

from apps.development.models.issue import STATE_CLOSED
from apps.payroll.models import Salary
from tests.base import trigger_on_commit, model_to_dict_form
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.factories import UserFactory


@pytest.fixture
def model_admin(db):
    yield site._registry[Salary]


def test_salary_instance_str(db):
    user = UserFactory.create()
    salary = SalaryFactory.create(user=user)

    assert str(salary) == f'{user} [{salary.created_at}]: {salary.sum}'


def test_get_urls(model_admin):
    assert 'generate-salaries' in [p.name for p in model_admin.get_urls()]


def test_generate_salaries_get_form(model_admin, admin_client):
    issue = IssueFactory.create(state=STATE_CLOSED)
    IssueSpentTimeFactory.create(
        user=UserFactory.create(),
        base=issue,
        time_spent=timedelta(hours=5).total_seconds()
    )

    url = f'/admin/payroll/salary/'

    response = model_admin.generate_salaries(
        admin_client.request_get(url)
    )

    assert response.status_code == status.HTTP_200_OK
    assert Salary.objects.count() == 0
    assert b'/admin/payroll/salary/generate/' in response.content
    assert b'period_from' in response.content
    assert b'period_to' in response.content


def test_generate_salaries(model_admin, admin_client):
    user = UserFactory.create()

    issue = IssueFactory.create(state=STATE_CLOSED)
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=5).total_seconds()
    )

    url = f'/admin/payroll/salary/'
    data = {
        'period_from': str(timezone.now().date() - timedelta(days=15)),
        'period_to': str(timezone.now().date())
    }

    response = model_admin.generate_salaries(
        admin_client.request_post(url, data)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert Salary.objects.count() == 1

    salary = Salary.objects.first()
    assert salary.total == user.hour_rate * 5
    assert salary.period_from == timezone.now().date() - timedelta(days=15)
    assert salary.period_to == timezone.now().date()


def test_send_notification(model_admin, admin_client):
    user = UserFactory.create(email='test1@mail.com')

    salary = SalaryFactory.create(user=user, payed=False)
    salary.payed = True

    SalaryFactory.create_batch(3, user=user, payed=False)
    SalaryFactory.create_batch(2, user=user, payed=True)

    url = f'/admin/payroll/salary/{salary.id}/change/'
    data = model_to_dict_form(salary)

    model_admin.changeform_view(
        admin_client.request_post(url, data),
        object_id=str(salary.id)
    )

    trigger_on_commit()
    salary.refresh_from_db()

    assert salary.payed is True
    assert len(mail.outbox) == 1
    assert mail.outbox[0].body is not None
    assert mail.outbox[0].from_email == settings.SERVER_EMAIL
    assert mail.outbox[0].to == [user.email]


def test_salary_payed_changed_to_false(model_admin, admin_client):
    user = UserFactory.create(email='test@mail.com')

    salary = SalaryFactory.create(user=user, payed=True)
    salary.payed = False

    url = f'/admin/payroll/salary/{salary.id}/change/'
    data = model_to_dict_form(salary)

    model_admin.changeform_view(
        admin_client.request_post(url, data),
        object_id=str(salary.id)
    )

    trigger_on_commit()
    salary.refresh_from_db()

    assert salary.payed is False
    assert len(mail.outbox) == 0


def test_user_without_email_but_payed(model_admin, admin_client):
    user = UserFactory.create()
    salary = SalaryFactory.create(user=user, payed=False)
    salary.payed = True

    url = f'/admin/payroll/salary/{salary.id}/change/'
    data = model_to_dict_form(salary)

    model_admin.changeform_view(
        admin_client.request_post(url, data),
        object_id=str(salary.id)
    )

    trigger_on_commit()
    salary.refresh_from_db()

    assert salary.payed is True
    assert len(mail.outbox) == 0


def test_salary_another_field_changed(model_admin, admin_client):
    user = UserFactory.create(email='test@mail.com')
    salary = SalaryFactory.create(user=user, payed=False)
    salary.sum = 10.0

    url = f'/admin/payroll/salary/{salary.id}/change/'
    data = model_to_dict_form(salary)

    model_admin.changeform_view(
        admin_client.request_post(url, data),
        object_id=str(salary.id)
    )

    trigger_on_commit()
    salary.refresh_from_db()

    assert salary.sum == 10.0
    assert len(mail.outbox) == 0


def test_salary_another_field_changed_and_payed(model_admin, admin_client):
    user = UserFactory.create(email='test@mail.com')
    salary = SalaryFactory.create(user=user, payed=False)
    salary.sum = 10.0
    salary.payed = True

    url = f'/admin/payroll/salary/{salary.id}/change/'
    data = model_to_dict_form(salary)

    model_admin.changeform_view(
        admin_client.request_post(url, data),
        object_id=str(salary.id)
    )

    trigger_on_commit()
    salary.refresh_from_db()

    assert salary.sum == 10.0
    assert salary.payed is True
    assert len(mail.outbox) == 1
