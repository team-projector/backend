from apps.payroll.graphql.filters import SalaryFilterSet
from apps.payroll.graphql.types import SalaryType
from apps.payroll.models.salary import Salary
from tests.helpers.objects import AttrDict
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_salary(user, client):
    team = TeamFactory.create()
    TeamMemberFactory.create(team=team, user=user)
    salary = SalaryFactory.create(user=user)

    client.user = user
    info = AttrDict({'context': client})

    assert SalaryType().get_node(info, salary.id) == salary


def test_salary_another_user(user, client):
    salary = SalaryFactory.create(user=user)

    user_2 = UserFactory()
    SalaryFactory.create_batch(size=5, user=user_2)

    team = TeamFactory.create()
    team.members.set([user, user_2])

    client.user = user
    info = AttrDict({'context': client})

    assert SalaryType().get_node(info, salary.id) == salary

    info.context.user = user_2

    assert SalaryType().get_node(info, salary.id) is None


def test_list(user, client):
    SalaryFactory.create_batch(size=5, user=user)

    client.user = user
    info = AttrDict({'context': client})

    salaries = SalaryType().get_queryset(Salary.objects.all(), info)

    assert salaries.count() == 5


def test_list_another_user(user, client):
    SalaryFactory.create_batch(size=2, user=user)

    user_2 = UserFactory()
    SalaryFactory.create_batch(size=5, user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    salaries = SalaryType().get_queryset(Salary.objects.all(), info)

    results = SalaryFilterSet(
        data={'user': user_2.id},
        queryset=salaries,
        request=client,
    ).qs

    assert results.count() == 0
