# -*- coding: utf-8 -*-

from apps.payroll.models import SpentTime
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_my_spents(user):
    spents = IssueSpentTimeFactory.create_batch(size=3, user=user)

    IssueSpentTimeFactory.create_batch(size=5, user=UserFactory.create())

    assert set(SpentTime.objects.allowed_for_user(user)) == set(spents)


def test_in_team_not_viewer(user, team, make_team_developer):
    user2 = UserFactory.create()
    make_team_developer(team, user)
    make_team_developer(team, user2)

    IssueSpentTimeFactory.create(user=user2)

    assert not SpentTime.objects.allowed_for_user(user).exists()


def test_as_team_leader(team_developer, team_leader):
    spent = IssueSpentTimeFactory.create(user=team_developer)

    assert list(SpentTime.objects.allowed_for_user(team_leader)) == [spent]


def test_as_team_watcher(team_developer, team_watcher):
    spent = IssueSpentTimeFactory.create(user=team_developer)

    assert list(SpentTime.objects.allowed_for_user(team_watcher)) == [spent]


def test_as_leader_another_team(user, make_team_developer, team_leader):
    team = TeamFactory.create()
    make_team_developer(team, user)

    IssueSpentTimeFactory.create(user=user)

    assert not SpentTime.objects.allowed_for_user(team_leader).exists()


def test_as_watcher_another_team(user, make_team_developer, team_watcher):
    team = TeamFactory.create()
    make_team_developer(team, user)

    IssueSpentTimeFactory.create(user=user)

    assert not SpentTime.objects.allowed_for_user(team_watcher).exists()


def test_my_spents_and_as_leader(
    user, make_team_developer, team_developer, team_leader,
):
    team = TeamFactory.create()
    make_team_developer(team, team_leader)

    spents = {
        *IssueSpentTimeFactory.create_batch(size=3, user=team_leader),
        *IssueSpentTimeFactory.create_batch(size=3, user=team_developer),
    }

    assert set(SpentTime.objects.allowed_for_user(team_leader)) == spents
