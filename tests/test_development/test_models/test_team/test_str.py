# -*- coding: utf-8 -*-

from tests.test_development.factories import TeamFactory


def test_str(db):
    team = TeamFactory.create(title="team_title_test")

    assert str(team) == "team_title_test"
