# -*- coding: utf-8 -*-

import pytest

from apps.development.api.views import GlWebhookView


@pytest.fixture(autouse=True)
def _gitlab_webhook_secret_token(override_config) -> None:
    """Set test gitlab token."""
    with override_config(GITLAB_WEBHOOK_SECRET_TOKEN=None):
        yield


@pytest.fixture()
def gl_webhook_view():
    """Gitlab webhook view."""
    return GlWebhookView.as_view()
