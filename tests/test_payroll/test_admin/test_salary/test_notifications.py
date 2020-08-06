# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import mail

from tests.helpers import db, objects
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_send_notification(admin_rf, salary_admin):
    user = UserFactory.create(email="test1@mail.com")

    salary = SalaryFactory.create(user=user, payed=False)
    salary.payed = True

    SalaryFactory.create_batch(3, user=user, payed=False)
    SalaryFactory.create_batch(2, user=user, payed=True)

    salary_admin.changeform_view(
        admin_rf.post(
            "/admin/payroll/salary/{0}/change/".format(salary.pk),
            objects.model_to_dict_form(salary),
        ),
        object_id=str(salary.id),
    )

    db.trigger_on_commit()
    salary.refresh_from_db()

    assert salary.payed
    assert len(mail.outbox) == 1
    assert mail.outbox[0].body is not None
    assert mail.outbox[0].from_email == settings.SERVER_EMAIL
    assert mail.outbox[0].to == [user.email]


def test_payed_changed_to_false(admin_rf, salary_admin):
    user = UserFactory.create(email="test@mail.com")

    salary = SalaryFactory.create(user=user, payed=True)
    salary.payed = False

    salary_admin.changeform_view(
        admin_rf.post(
            "/admin/payroll/salary/{0}/change/".format(salary.pk),
            objects.model_to_dict_form(salary),
        ),
        object_id=str(salary.id),
    )

    db.trigger_on_commit()
    salary.refresh_from_db()

    assert not salary.payed
    assert not mail.outbox


def test_user_without_email_but_payed(admin_rf, salary_admin):
    user = UserFactory.create()
    salary = SalaryFactory.create(user=user, payed=False)
    salary.payed = True

    salary_admin.changeform_view(
        admin_rf.post(
            "/admin/payroll/salary/{0}/change/".format(salary.pk),
            objects.model_to_dict_form(salary),
        ),
        object_id=str(salary.id),
    )

    db.trigger_on_commit()
    salary.refresh_from_db()

    assert salary.payed
    assert not mail.outbox


def test_another_field_changed(admin_rf, salary_admin):
    user = UserFactory.create(email="test@mail.com")
    salary = SalaryFactory.create(user=user, payed=False)
    salary.sum = 10.0  # noqa: WPS125, A003, A002

    salary_admin.changeform_view(
        admin_rf.post(
            "/admin/payroll/salary/{0}/change/".format(salary.pk),
            objects.model_to_dict_form(salary),
        ),
        object_id=str(salary.id),
    )

    db.trigger_on_commit()
    salary.refresh_from_db()

    assert salary.sum == 10.0
    assert not mail.outbox


def test_another_field_changed_and_payed(admin_rf, salary_admin):
    user = UserFactory.create(email="test@mail.com")
    salary = SalaryFactory.create(user=user, payed=False)
    salary.sum = 10.0  # noqa: WPS125, A003, A002
    salary.payed = True

    salary_admin.changeform_view(
        admin_rf.post(
            "/admin/payroll/salary/{0}/change/".format(salary.pk),
            objects.model_to_dict_form(salary),
        ),
        object_id=str(salary.id),
    )

    db.trigger_on_commit()
    salary.refresh_from_db()

    assert salary.sum == 10.0
    assert salary.payed
    assert len(mail.outbox) == 1
