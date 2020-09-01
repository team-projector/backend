# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)
def _gitlab_token(override_config) -> None:
    """Set test gitlab token."""
    with override_config(GITLAB_TOKEN="GITLAB_TOKEN"):
        yield
