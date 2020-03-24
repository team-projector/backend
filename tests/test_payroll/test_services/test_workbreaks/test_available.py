# -*- coding: utf-8 -*-

from apps.payroll.models import WorkBreak
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_my_work_breaks(user):
    work_breaks = WorkBreakFactory.create_batch(size=3, user=user)

    WorkBreakFactory.create_batch(size=5, user=UserFactory.create())

    assert set(WorkBreak.objects.allowed_for_user(user)) == set(work_breaks)


def test_in_team_not_viewer(user, team, make_team_developer):
    user_2 = UserFactory.create()
    make_team_developer(team, user_2)
    make_team_developer(team, user)

    WorkBreakFactory.create(user=user_2)

    assert not WorkBreak.objects.allowed_for_user(user).exists()


def test_as_team_leader(team_leader, team_developer):
    work_break = WorkBreakFactory.create(user=team_developer)

    assert list(WorkBreak.objects.allowed_for_user(team_leader)) == [
        work_break
    ]


def test_as_team_watcher(team_watcher, team_developer):
    WorkBreakFactory.create(user=team_developer)

    assert not WorkBreak.objects.allowed_for_user(team_watcher).exists()


def test_as_leader_another_team(user, make_team_leader, team_developer):
    make_team_leader(TeamFactory.create(), user)

    WorkBreakFactory.create(user=team_developer)

    assert not WorkBreak.objects.allowed_for_user(user).exists()


def test_as_watcher_another_team(user, make_team_watcher, team_developer):
    make_team_watcher(TeamFactory.create(), user)

    WorkBreakFactory.create(user=team_developer)

    assert not WorkBreak.objects.allowed_for_user(user).exists()


def test_my_work_breaks_and_as_leader(
    user, make_team_leader, team, team_developer,
):
    make_team_leader(team, user)

    work_breaks = {
        *WorkBreakFactory.create_batch(size=3, user=user),
        *WorkBreakFactory.create_batch(size=3, user=team_developer),
    }

    assert set(WorkBreak.objects.allowed_for_user(user)) == work_breaks


def test_double_work_breaks(user, make_team_leader):
    work_breaks = WorkBreakFactory.create_batch(size=10, user=user)

    make_team_leader(TeamFactory.create(), user)
    make_team_leader(TeamFactory.create(), user)

    assert set(WorkBreak.objects.allowed_for_user(user)) == set(work_breaks)
