# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)  # type: ignore
def _gitlab_webhook_secret_token(settings) -> None:
    """Set test gitlab token."""
    settings.GITLAB_WEBHOOK_SECRET_TOKEN = None
