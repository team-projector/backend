from constance.test import override_config
from django.core import mail

from apps.payroll.tasks.salaries import send_salary_email_report_task
from settings.components.constance import Currency
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


@override_config(DEFAULT_FROM_EMAIL="foo@bar")
def test_send_salary_email_report(db):
    """
    Test send salary email report.

    :param db:
    """
    user = UserFactory.create(email="test1@mail.com")

    salary = SalaryFactory.create(user=user, payed=True)

    SalaryFactory.create_batch(3, user=user, payed=False)

    assert not mail.outbox

    send_salary_email_report_task(salary.id)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].body is not None
    assert mail.outbox[0].from_email == "foo@bar"
    assert mail.outbox[0].to == [user.email]


def test_without_email(db):
    """
    Test without email.

    :param db:
    """
    user = UserFactory.create(email="")

    salary = SalaryFactory.create(user=user, payed=True)
    SalaryFactory.create_batch(3, user=user, payed=False)

    assert not mail.outbox

    send_salary_email_report_task(salary.id)

    assert not mail.outbox


@override_config(CURRENCY_CODE=Currency.RUR, DEFAULT_FROM_EMAIL="foo@bar")
def test_send_report_with_rur(db):
    """Test send report."""
    user = UserFactory.create(email="test1@mail.com")
    salary = SalaryFactory.create(user=user, payed=True)
    SalaryFactory.create_batch(3, user=user, payed=False)

    send_salary_email_report_task(salary.id)

    assert len(mail.outbox) == 1

    send_mail = mail.outbox[0]

    assert send_mail.body is not None
    assert Currency.RUR.label in send_mail.alternatives[0][0]
