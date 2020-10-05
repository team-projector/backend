# -*- coding: utf-8 -*-

from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.allowed import filter_allowed_for_user
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_by_assignee(user):
    """
    Test by assignee.

    :param user:
    """
    another_user = UserFactory.create()

    IssueSpentTimeFactory.create_batch(4, user=user)
    IssueSpentTimeFactory.create_batch(2, user=another_user)

    allowed = filter_allowed_for_user(SpentTime.objects.all(), user)

    assert allowed.count() == 4


def test_by_team_leader(team_developer, team_leader):
    """
    Test by team leader.

    :param team_developer:
    :param team_leader:
    """
    IssueSpentTimeFactory.create_batch(4, user=team_developer)
    allowed = filter_allowed_for_user(SpentTime.objects.all(), team_leader)

    assert allowed.count() == 4


def test_by_team_leader_and_user(team_developer, team_leader):
    """
    Test by team leader and user.

    :param team_developer:
    :param team_leader:
    """
    IssueSpentTimeFactory.create_batch(4, user=team_developer)
    IssueSpentTimeFactory.create_batch(3, user=team_leader)

    allowed = filter_allowed_for_user(SpentTime.objects.all(), team_leader)

    assert allowed.count() == 7


def test_by_team_watcher(team_developer, team_watcher):
    """
    Test by team watcher.

    :param team_developer:
    :param team_watcher:
    """
    IssueSpentTimeFactory.create_batch(4, user=team_developer)

    allowed = filter_allowed_for_user(SpentTime.objects.all(), team_watcher)

    assert allowed.count() == 4
