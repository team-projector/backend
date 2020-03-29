# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)
def _weekends_days(settings) -> None:
    """Set test gitlab token."""
    settings.TP_WEEKENDS_DAYS = []
