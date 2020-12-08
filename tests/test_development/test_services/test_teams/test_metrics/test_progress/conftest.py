import pytest

from tests.test_users.factories import UserFactory


@pytest.fixture(autouse=True)
def _weekends_days(override_config) -> None:
    """Set test gitlab token."""
    with override_config(WEEKENDS_DAYS=[]):
        yield


@pytest.fixture()
def another_user(db):
    """Create another user."""
    return UserFactory.create()
