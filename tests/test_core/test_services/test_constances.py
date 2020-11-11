import pytest
from constance.test import override_config

from apps.core.services.constances import WEEK_DAY_MAP, get_first_week_day


@pytest.fixture(params=[0, 1, "1", "0"])
def first_day(request):
    """Override config for user."""
    with override_config(FIRST_WEEK_DAY=request.param):
        yield request.param


def test_get_first_week_day(first_day):
    """Test get first week day."""
    assert WEEK_DAY_MAP.get(int(first_day)) == get_first_week_day()
