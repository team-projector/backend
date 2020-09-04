# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(autouse=True)
def _django_settings(settings, tmpdir_factory) -> None:
    """Forces django test settings."""
    settings.MEDIA_ROOT = tmpdir_factory.mktemp("media", numbered=True)
    settings.DOMAIN_NAME = "https://teamprojector.com"
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    settings.STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    settings.CONSTANCE_BACKEND = "constance.backends.memory.MemoryBackend"


@pytest.fixture(autouse=True)
def _constance_config(override_config) -> None:
    """Forces constance config."""
    with override_config(GITLAB_ADDRESS="https://gitlab.com"):
        yield
