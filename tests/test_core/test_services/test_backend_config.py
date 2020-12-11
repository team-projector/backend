import json
from unittest.mock import MagicMock

import factory
import pytest
from factory.fuzzy import FuzzyChoice

from apps.core.services.backend_config import (
    CONSTANCE_CONFIG_MAPPING,
    BackendConfig,
    BackendConfigService,
    Currency,
    constance_config_provider,
)


class _MockedCache:
    def __init__(self, return_value=None):
        self.add = MagicMock()
        self.get = MagicMock(return_value=return_value)


class _BackendConfigFactory(factory.Factory):
    class Meta:
        model = BackendConfig

    firstWeekDay = FuzzyChoice([0, 1])  # noqa: WPS115, N815
    currencyCode = FuzzyChoice(Currency)  # noqa: WPS115, N815
    gitlabLoginEnabled = factory.Faker("boolean")  # noqa: WPS115, N815
    demoMode = factory.Faker("boolean")  # noqa: WPS115, N815
    staticHead = factory.Faker("text")  # noqa: WPS115, N815


@pytest.mark.parametrize(
    "provider",
    [_BackendConfigFactory.create, constance_config_provider],
)
def test_providers(provider):
    """Test config_provider."""
    config = provider()
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        config_provider=lambda: config,
        cache_key="config",
        expire_after=10,
    )
    assert service.get_config() == "backend = {0}".format(
        json.dumps({"config": config}),
    )


def test_cached():
    """Test a cache is properly used for serving config."""
    cache_key = "config"
    cache = _MockedCache()
    service = BackendConfigService(
        cache_manager=cache,
        config_provider=_BackendConfigFactory.create,
        cache_key=cache_key,
        expire_after=10,
    )
    config = service.get_config()

    assert cache.get.call_args.args == (cache_key,)
    assert cache.add.call_args.args == (cache_key, config)
    assert cache.add.call_args.kwargs["timeout"] == 10


@pytest.mark.parametrize(
    "config_key",
    [
        "firstWeekDay",
        "currencyCode",
        "gitlabLoginEnabled",
        "demoMode",
        "staticHead",
    ],
)
def test_constance_provider_alter_value(override_config, config_key):
    """Test config is depends on constance variables."""
    backend_config = _BackendConfigFactory.create()
    constance_key = CONSTANCE_CONFIG_MAPPING[config_key]
    with override_config(**{constance_key: backend_config[config_key]}):
        assert (
            constance_config_provider()[config_key]
            == backend_config[config_key]
        )
