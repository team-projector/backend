import pytest

from apps.core.gitlab.parsers import parse_state_merged


def test_success():
    """Test success."""
    assert parse_state_merged([{"state": "merged"}])


@pytest.mark.parametrize(
    "states",
    [[], [{"state": "opened"}], [{"state": "bla"}]],
)
def test_fail(states):
    """
    Test fail.

    :param states:
    """
    assert not parse_state_merged(states)
