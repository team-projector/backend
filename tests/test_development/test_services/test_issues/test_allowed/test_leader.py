# -*- coding: utf-8 -*-

from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_issues.test_allowed import (
    helpers,
)


def test_leader(team_leader, team_developer):
    """
    Test leader.

    :param team_leader:
    :param team_developer:
    """
    helpers.check_allowed_for_user(
        team_leader,
        IssueFactory.create_batch(4, user=team_developer),
    )


def test_leader_and_developer(team_leader, team_developer):
    """
    Test leader and developer.

    :param team_leader:
    :param team_developer:
    """
    helpers.check_allowed_for_user(
        team_leader,
        [
            *IssueFactory.create_batch(4, user=team_developer),
            *IssueFactory.create_batch(3, user=team_leader),
        ],
    )
