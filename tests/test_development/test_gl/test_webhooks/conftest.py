# -*- coding: utf-8 -*-

import pytest

from apps.development.api.views import GlWebhookView


@pytest.fixture(autouse=True)  # type: ignore
def _gitlab_webhook_secret_token(settings) -> None:
    """Set test gitlab token."""
    settings.GITLAB_WEBHOOK_SECRET_TOKEN = None


@pytest.fixture()
def gl_webhook_view():
    """Gitlab webhook view."""
    return GlWebhookView.as_view()
