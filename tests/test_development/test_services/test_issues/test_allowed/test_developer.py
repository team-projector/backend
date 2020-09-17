# -*- coding: utf-8 -*-

from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_issues.test_allowed import (
    helpers,
)


def test_only_my(team_developer):
    """
    Test only my.

    :param team_developer:
    """
    helpers.check_allowed_for_user(
        team_developer,
        IssueFactory.create_batch(2, user=team_developer),
    )


def test_exclude_another_developer(team, team_developer, make_team_developer):
    """
    Test exclude another developer.

    :param team:
    :param team_developer:
    :param make_team_developer:
    """
    IssueFactory.create_batch(2, user=make_team_developer(team))

    helpers.check_allowed_for_user(
        team_developer,
        IssueFactory.create_batch(2, user=team_developer),
    )
