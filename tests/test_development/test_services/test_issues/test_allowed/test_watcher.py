# -*- coding: utf-8 -*-

from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_issues.test_allowed import (
    helpers,
)


def test_watcher(team_watcher, team_developer):
    helpers.check_allowed_for_user(
        team_watcher,
        IssueFactory.create_batch(4, user=team_developer),
    )
