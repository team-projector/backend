# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)  # type: ignore
def _gitlab_token(settings) -> None:
    """Set test gitlab token."""
    settings.GITLAB_TOKEN = "GITLAB_TOKEN"
