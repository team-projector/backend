from tests.test_payroll.factories import SalaryFactory


def test_str(user):
    salary = SalaryFactory.create(user=user, sum=150)

    assert str(salary) == "{0} [{1}]: 150".format(
        user.login, salary.created_at,
    )
