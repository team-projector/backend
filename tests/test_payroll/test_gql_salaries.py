from apps.development.models import TeamMember
from apps.payroll.graphql.filters import SalaryFilterSet
from apps.payroll.graphql.types import SalaryType
from apps.payroll.models.salary import Salary
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


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


def test_salaries_filter_by_user(user, client):
    user_2 = UserFactory.create()
    salaries_user_2 = SalaryFactory.create_batch(size=5, user=user_2)

    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.leader
    )

    client.user = user
    info = AttrDict({'context': client})

    salaries = SalaryType().get_queryset(Salary.objects.all(), info)

    results = SalaryFilterSet(
        data={'user': user_2.id},
        queryset=salaries,
        request=client,
    ).qs

    assert results.count() == 5
    assert set(results) == set(salaries_user_2)


def test_salaries_filter_by_team(user, client):
    user_2 = UserFactory.create()
    salaries_user_2 = SalaryFactory.create_batch(size=2, user=user_2)

    user_3 = UserFactory.create()
    SalaryFactory.create_batch(size=3, user=user_3)

    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user, team=team).update(
        roles=TeamMember.roles.leader)

    client.user = user
    info = AttrDict({'context': client})

    salaries = SalaryType().get_queryset(Salary.objects.all(), info)

    results = SalaryFilterSet(
        data={'team': team.id},
        queryset=salaries,
        request=client,
    ).qs

    assert results.count() == 2
    assert set(results) == set(salaries_user_2)


def test_double_salaries(user, client):
    salaries = SalaryFactory.create_batch(size=10, user=user)

    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader
    )
    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader
    )

    client.user = user
    info = AttrDict({'context': client})

    queryset = SalaryType().get_queryset(Salary.objects.all(), info)

    results = SalaryFilterSet(
        data={'user': user.id},
        queryset=queryset,
        request=client,
    ).qs

    assert results.count() == 10
    assert set(results) == set(salaries)
