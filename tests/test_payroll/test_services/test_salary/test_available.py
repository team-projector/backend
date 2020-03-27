# -*- coding: utf-8 -*-

from apps.payroll.models import Salary
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_my_salaries(user):
    SalaryFactory.create_batch(size=5, user=UserFactory.create())
    salaries = SalaryFactory.create_batch(size=3, user=user)

    assert set(Salary.objects.allowed_for_user(user)) == set(salaries)


def test_in_team_not_viewer(user):
    user2 = UserFactory.create()
    TeamFactory.create(members=[user, user2])
    SalaryFactory.create(user=user2)

    assert not Salary.objects.allowed_for_user(user).exists()


def test_as_team_leader(team_developer, team_leader):
    salary = SalaryFactory.create(user=team_developer)

    assert list(Salary.objects.allowed_for_user(team_leader)) == [salary]


def test_as_team_watcher(team_developer, team_watcher):
    SalaryFactory.create(user=team_developer)

    assert not Salary.objects.allowed_for_user(team_watcher).exists()


def test_as_leader_another_team(user, team_leader):
    user2 = UserFactory.create()
    TeamFactory.create(members=[user2])
    SalaryFactory.create(user=user2)

    assert not Salary.objects.allowed_for_user(team_leader).exists()


def test_as_watcher_another_team(user, team_watcher):
    user2 = UserFactory.create()
    TeamFactory.create(members=[user2])
    SalaryFactory.create(user=user2)

    assert not Salary.objects.allowed_for_user(team_watcher).exists()


def test_my_salaries_and_as_leader(team_leader, team_developer):
    TeamFactory.create(members=[team_leader])

    salaries = {
        *SalaryFactory.create_batch(size=3, user=team_leader),
        *SalaryFactory.create_batch(size=3, user=team_developer),
    }

    assert set(Salary.objects.allowed_for_user(team_leader)) == salaries


def test_my_salaries_and_as_leader_with_queryset(team_leader, team_developer):
    TeamFactory.create(members=[team_leader])

    another_user = UserFactory.create()

    SalaryFactory.create_batch(size=3, user=team_leader)
    SalaryFactory.create_batch(size=3, user=team_developer)
    SalaryFactory.create_batch(size=3, user=another_user)

    queryset = Salary.objects.filter(user=another_user)

    assert (
        queryset.filter(
            id__in=Salary.objects.allowed_for_user(team_leader),
        ).count()
        == 0
    )
