import json
import types
from typing import Callable, TypedDict

from constance import config
from constance.signals import config_updated
from django.core.cache import BaseCache, cache
from django.dispatch import receiver

from settings.components.constance import Currency

_CACHE_KEY = "backend_config"
_CACHE_EXPIRE_AFTER = 60 * 60  # seconds

CONSTANCE_CONFIG_MAPPING = types.MappingProxyType(
    {
        "firstWeekDay": "FIRST_WEEK_DAY",
        "currencyCode": "CURRENCY_CODE",
        "gitlabLoginEnabled": "GITLAB_LOGIN_ENABLED",
        "demoMode": "DEMO_MODE",
        "staticHead": "STATIC_HEAD",
    },
)


@receiver(config_updated)
def _flush_backend_config_cache(sender, key, old_value, new_value, **kwargs):
    constance_keys = CONSTANCE_CONFIG_MAPPING.values()

    if key not in constance_keys:
        return
    cache.delete(_CACHE_KEY)


class BackendConfig(TypedDict):
    """Backend config dict."""

    firstWeekDay: int  # noqa: WPS115, N815
    currencyCode: Currency  # noqa: WPS115, N815
    gitlabLoginEnabled: bool  # noqa: WPS115, N815
    demoMode: bool  # noqa: WPS115, N815
    staticHead: str  # noqa: WPS115, N815


class BackendConfigService:
    """Generates config.js file content required for angular app setup."""

    def __init__(
        self,
        cache_manager: BaseCache,
        config_provider: Callable[[], BackendConfig],
        cache_key: str,
        expire_after: int,
    ):
        """Inject dependencies."""
        self._cache_key = cache_key
        self._expire_after = expire_after
        self._cache = cache_manager
        self._config_provider = config_provider

    def get_config(self):
        """:returns config content."""
        config_file_content = self._cache.get(self._cache_key)
        if not config_file_content:
            config_file_content = "backend = {0}".format(
                json.dumps({"config": self._config_provider()}),
            )
        self._cache.add(
            self._cache_key,
            config_file_content,
            timeout=self._expire_after,
        )
        return config_file_content


def constance_config_provider() -> BackendConfig:
    """Maps constance keys to BackendConfig."""
    return BackendConfig(  # type: ignore
        **{
            service_key: getattr(config, constance_key)
            for service_key, constance_key in CONSTANCE_CONFIG_MAPPING.items()
        },
    )


get_config = BackendConfigService(
    cache_manager=cache,
    config_provider=constance_config_provider,
    cache_key=_CACHE_KEY,
    expire_after=_CACHE_EXPIRE_AFTER,
).get_config
