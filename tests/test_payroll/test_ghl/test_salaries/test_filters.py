import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from apps.payroll.graphql.filters import SalaryFilterSet
from apps.payroll.models.salary import Salary
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_salaries_filter_by_user(user):
    SalaryFactory.create_batch(size=3, user=user)

    user_2 = UserFactory.create()
    salaries_user_2 = SalaryFactory.create_batch(size=5, user=user_2)

    results = SalaryFilterSet(
        data={"user": user_2.id}, queryset=Salary.objects.all(),
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
        roles=TeamMember.roles.LEADER
    )

    client.user = user

    results = SalaryFilterSet(
        data={"team": team.id}, queryset=Salary.objects.all(), request=client,
    ).qs

    assert results.count() == 2
    assert set(results) == set(salaries_user_2)


def test_salaries_filter_by_team_not_leader(user, client):
    user_2 = UserFactory.create()
    SalaryFactory.create_batch(size=2, user=user_2)

    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user, team=team).update(
        roles=TeamMember.roles.DEVELOPER
    )

    client.user = user

    with pytest.raises(GraphQLPermissionDenied):
        SalaryFilterSet(  # noqa: WPS428
            data={"team": team.id},
            queryset=Salary.objects.all(),
            request=client,
        ).qs
