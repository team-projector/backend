# -*- coding: utf-8 -*-

from apps.payroll.graphql.filters import PenaltyFilterSet
from apps.payroll.models import Penalty
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import PenaltyFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_penalties_filter_by_user(user):
    """
    Test penalties filter by user.

    :param user:
    """
    PenaltyFactory.create_batch(size=3, user=user)

    user2 = UserFactory.create()
    penalties_user2 = PenaltyFactory.create_batch(size=5, user=user2)

    queryset = PenaltyFilterSet(
        data={"user": user2.id},
        queryset=Penalty.objects.all(),
    ).qs

    assert queryset.count() == 5
    assert set(queryset) == set(penalties_user2)


def test_penalties_filter_by_salary(user):
    """
    Test penalties filter by salary.

    :param user:
    """
    salary = SalaryFactory(user=user)
    PenaltyFactory.create_batch(size=3, user=user)
    penalties_salary2 = PenaltyFactory.create_batch(
        size=5,
        user=user,
        salary=salary,
    )

    queryset = PenaltyFilterSet(
        data={"salary": salary.id},
        queryset=Penalty.objects.all(),
    ).qs

    assert queryset.count() == 5
    assert set(queryset) == set(penalties_salary2)


def test_salary_is_null(user):
    """
    Test salary is null.

    :param user:
    """
    PenaltyFactory.create_batch(size=2, user=user, salary=None)

    queryset = PenaltyFilterSet(
        data={"salary": None},
        queryset=Penalty.objects.all(),
    ).qs

    assert queryset.count() == 2


def test_penalties_filter_by_team(user):
    """Test filter penalties by team."""
    penalties = PenaltyFactory.create_batch(size=3, user=user)

    team = TeamFactory()
    TeamMemberFactory.create(user=user, team=team)

    PenaltyFactory.create_batch(size=5, user=UserFactory.create())

    queryset = PenaltyFilterSet(
        data={"team": team.id},
        queryset=Penalty.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert set(queryset) == set(penalties)


def test_penalties_filter_by_team_empty(user):
    """Test filter penalties by team is empty."""
    PenaltyFactory.create_batch(size=3, user=user)

    team = TeamFactory()
    TeamMemberFactory.create(user=UserFactory.create(), team=team)

    queryset = PenaltyFilterSet(
        data={"team": team.id},
        queryset=Penalty.objects.all(),
    ).qs

    assert not queryset.exists()
