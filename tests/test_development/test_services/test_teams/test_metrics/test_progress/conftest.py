import pytest


@pytest.fixture(autouse=True)
def _weekends_days(override_config) -> None:
    """Set test gitlab token."""
    with override_config(WEEKENDS_DAYS=[]):
        yield
