import pytest

from django.conf import settings
from django.contrib.admin import site
from django.core import mail

from apps.payroll.models.salary import Salary
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


@pytest.fixture
def model_admin(db):
    yield site._registry[Salary]


@pytest.mark.django_db(transaction=True)
def test_send_notification(model_admin):
    user_1 = UserFactory.create(email='test1@mail.com')
    salary_1 = SalaryFactory.create(user=user_1, payed=False)

    user_2 = UserFactory.create(email='test2@mail.com')
    salary_2 = SalaryFactory.create(user=user_2, payed=False)

    salary_1.payed = True
    salary_2.payed = True

    model_admin.save_model(request=None, obj=salary_1, form=None, change=True)
    model_admin.save_model(request=None, obj=salary_2, form=None, change=True)

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_1.email]
    assert mail.outbox[0].body is not None
    assert mail.outbox[0].from_email == settings.SERVER_EMAIL
    assert mail.outbox[1].to == [user_2.email]


def test_salary_payed_changed_to_false(model_admin):
    user = UserFactory.create(email='test@mail.com')
    salary = SalaryFactory.create(user=user, payed=True)
    salary.payed = False

    model_admin.save_model(request=None, obj=salary, form=None, change=True)

    salary.refresh_from_db()

    assert len(mail.outbox) == 0


def test_salary_payed_not_changed(model_admin):
    user = UserFactory.create(email='test@mail.com')
    salary = SalaryFactory.create(user=user, payed=True)
    salary.payed = True

    model_admin.save_model(request=None, obj=salary, form=None, change=True)

    assert len(mail.outbox) == 0


def test_salary_another_field_changed(model_admin):
    user = UserFactory.create(email='test@mail.com')
    salary = SalaryFactory.create(user=user, payed=False)
    salary.sum = 10.0

    model_admin.save_model(request=None, obj=salary, form=None, change=True)

    salary.refresh_from_db()

    assert salary.sum == 10.0
    assert len(mail.outbox) == 0


def test_user_without_email(model_admin):
    user = UserFactory.create()
    salary = SalaryFactory.create(user=user, payed=False)
    salary.payed = True

    model_admin.save_model(request=None, obj=salary, form=None, change=True)

    assert len(mail.outbox) == 0
