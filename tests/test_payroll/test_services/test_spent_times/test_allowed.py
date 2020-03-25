# -*- coding: utf-8 -*-

from apps.payroll.models import SpentTime
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_by_assignee(user):
    another_user = UserFactory.create()

    IssueSpentTimeFactory.create_batch(4, user=user)
    IssueSpentTimeFactory.create_batch(2, user=another_user)

    allowed = SpentTime.objects.allowed_for_user(user)

    assert allowed.count() == 4


def test_by_team_leader(team_developer, team_leader):
    IssueSpentTimeFactory.create_batch(4, user=team_developer)
    allowed = SpentTime.objects.allowed_for_user(team_leader)

    assert allowed.count() == 4


def test_by_team_leader_and_user(team_developer, team_leader):
    IssueSpentTimeFactory.create_batch(4, user=team_developer)
    IssueSpentTimeFactory.create_batch(3, user=team_leader)

    allowed = SpentTime.objects.allowed_for_user(team_leader)

    assert allowed.count() == 7


def test_by_team_watcher(team_developer, team_watcher):
    IssueSpentTimeFactory.create_batch(4, user=team_developer)

    allowed = SpentTime.objects.allowed_for_user(team_watcher)

    assert allowed.count() == 4