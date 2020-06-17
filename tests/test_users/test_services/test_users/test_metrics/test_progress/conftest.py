# -*- coding: utf-8 -*-

from datetime import datetime

import pytest
from freezegun import freeze_time


@pytest.fixture(autouse=True)
def _weekends_days(settings) -> None:
    """Set test gitlab token."""
    settings.TP_WEEKENDS_DAYS = []


@pytest.fixture()
def _freeze_to_noon():
    with freeze_time("{0} 12:00:00".format(datetime.now().date())):
        yield
