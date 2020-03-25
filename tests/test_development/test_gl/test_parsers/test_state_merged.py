# -*- coding: utf-8 -*-

import pytest

from apps.core.gitlab.parsers import parse_state_merged


def test_success():
    assert parse_state_merged([{"state": "merged"}])


@pytest.mark.parametrize(
    "states", [[], [{"state": "opened"}], [{"state": "bla"}]],
)
def test_fail(states):
    assert not parse_state_merged(states)
