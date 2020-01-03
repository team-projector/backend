from django.conf import settings
from django.core import mail

from apps.payroll.tasks.salaries import send_salary_email_report_task
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_send_salary_email_report(db):
    user = UserFactory.create(email="test1@mail.com")

    salary = SalaryFactory.create(user=user, payed=True)

    SalaryFactory.create_batch(3, user=user, payed=False)

    assert not mail.outbox

    send_salary_email_report_task(salary.id)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].body is not None
    assert mail.outbox[0].from_email == settings.SERVER_EMAIL
    assert mail.outbox[0].to == [user.email]


def test_without_email(db):
    user = UserFactory.create(email="")

    salary = SalaryFactory.create(user=user, payed=True)

    SalaryFactory.create_batch(3, user=user, payed=False)

    assert not mail.outbox

    send_salary_email_report_task(salary.id)

    assert not mail.outbox
