from unittest.mock import MagicMock

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

    assert config == (
        'backend = {"config": {"firstWeekDay": 0, "currencyCode": "usd"}}'
    )
    assert cache.get.call_args.args == ("config",)
    assert cache.add.call_args.args == ("config", config)
    assert cache.add.call_args.kwargs["timeout"] == 10


def test_config_alter_constance_value(override_config):
    """Test config is depends on constance variables."""
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        cache_key="config",
        expire_after=10,
    )
    with override_config(FIRST_WEEK_DAY=1):
        config = service.get_config()
    assert (
        config
        == 'backend = {"config": {"firstWeekDay": 1, "currencyCode": "usd"}}'
    )


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
    assert config == (
        'backend = {"config": {"firstWeekDay": 0, "currencyCode": "rur"}}'
    )
