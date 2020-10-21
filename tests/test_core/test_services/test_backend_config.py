import json
from unittest.mock import MagicMock

from django.conf import settings

from apps.core.services.backend_config import BackendConfigService


class _MockedCache:
    def __init__(self, return_value=None):
        self.add = MagicMock()
        self.get = MagicMock(return_value=return_value)


def test_cached():
    """Test a cache is properly used for serving config."""
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        cache_key="config",
        expire_after=10,
    )
    config = service.get_config()

    _assert_config(config)
    assert cache.get.call_args.args == ("config",)
    assert cache.add.call_args.args == ("config", config)
    assert cache.add.call_args.kwargs["timeout"] == 10


def test_config_alter_constance_first_day(override_config):
    """Test config is depends on constance variables."""
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        cache_key="config",
        expire_after=10,
    )
    with override_config(FIRST_WEEK_DAY=1):
        config = service.get_config()

    _assert_constance_value(config, "firstWeekDay", 1)


def test_config_alter_constance_value_currency(override_config):
    """Test config is depends on constance variables."""
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        cache_key="config",
        expire_after=10,
    )
    with override_config(CURRENCY_CODE="rur"):
        config = service.get_config()

    _assert_constance_value(config, "currencyCode", "rur")


def test_config_alter_constance_login_enabled(override_config):
    """Test config is depends on constance variables."""
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        cache_key="config",
        expire_after=10,
    )
    with override_config(GITLAB_LOGIN_ENABLED=False):
        config = service.get_config()

    _assert_constance_value(
        config,
        "gitlabLoginEnabled",
        False,  # noqa: WPS425
    )


def _assert_config(config):
    constances = settings.CONSTANCE_CONFIG
    _assert_constance_value(
        config,
        "firstWeekDay",
        constances["FIRST_WEEK_DAY"][0],
    )
    _assert_constance_value(
        config,
        "currencyCode",
        constances["CURRENCY_CODE"][0],
    )
    _assert_constance_value(
        config,
        "gitlabLoginEnabled",
        constances["GITLAB_LOGIN_ENABLED"][0],
    )


def _assert_constance_value(config, key_name, constance_value):
    backend = json.loads(config.replace("backend = ", ""))

    assert key_name in backend["config"]
    assert backend["config"][key_name] == constance_value
