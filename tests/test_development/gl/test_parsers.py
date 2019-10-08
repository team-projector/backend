from apps.development.services.gitlab.parsers import (
    parse_gl_date,
    parse_gl_datetime,
    parse_state_merged,
)


def test_parse_gl_datetime():
    assert parse_gl_datetime('') is None

    gl_datetime = '2000-01-01T12:00:00.000000Z'

    assert parse_gl_datetime(gl_datetime) is not None


def test_parse_gl_date():
    assert parse_gl_date('') is None

    gl_date = '2000-01-01'

    assert parse_gl_date(gl_date) is not None


def test_parse_state_merged():
    assert parse_state_merged([]) is False

    states = [{'state': 'opened'}]

    assert parse_state_merged(states) is False

    states = [{'state': 'merged'}]

    assert parse_state_merged(states) is True
