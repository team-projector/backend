# -*- coding: utf-8 -*-

from datetime import timedelta

import pytest

from apps.development.services.note.gl.parsers.base import parse_spend


@pytest.mark.parametrize(
    ("spent", "expected"),
    [
        ("1d 1m", timedelta(hours=8, minutes=1)),
        (" 1d  1m  5s", timedelta(hours=8, minutes=1, seconds=5)),
        ("1m", timedelta(minutes=1)),
        ("1d 30m", timedelta(hours=8, minutes=30)),
        ("1d 30m 15s", timedelta(hours=8, minutes=30, seconds=15)),
        ("2w 2d 4h", timedelta(hours=100)),  # 2*5d * 8h + 2*8h + 4h
        ("2mo 2d 4h", timedelta(hours=340)),  # 2*4w*5d*8*h + 2*8h + 4h
        ("0", timedelta(seconds=0)),
        ("", timedelta(seconds=0)),
        (None, timedelta(seconds=0)),
    ],
)
def test_parse(spent, expected):
    """
    Test parse.

    :param spent:
    :param expected:
    """
    expected_secs = expected.total_seconds()

    assert parse_spend(spent) == expected_secs, "{0} = {1} secs".format(
        spent, expected_secs,
    )
