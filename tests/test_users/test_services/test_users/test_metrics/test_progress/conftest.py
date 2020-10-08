from datetime import datetime

import pytest
from freezegun import freeze_time


@pytest.fixture(autouse=True)
def _weekends_days(override_config) -> None:
    """Set test gitlab token."""
    with override_config(WEEKENDS_DAYS=[]):
        yield


@pytest.fixture()
def _freeze_to_noon():
    """Freeze to noon."""
    with freeze_time("{0} 12:00:00".format(datetime.now().date())):
        yield
