# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)  # type: ignore
def _weekends_days(settings) -> None:
    """Set test gitlab token."""
    settings.TP_WEEKENDS_DAYS = []
