import json
from typing import Dict

from constance import config
from constance.signals import config_updated
from django.core.cache import BaseCache, cache
from django.dispatch import receiver

_CACHE_KEY = "backend_config"
_CACHE_EXPIRE_AFTER = 60 * 60  # seconds


@receiver(config_updated)
def _flush_backend_config_cache(sender, key, old_value, new_value, **kwargs):
    if key != "FIRST_WEEK_DAY":
        return
    cache.delete(_CACHE_KEY)


class BackendConfigService:
    """Generates config.js file content required for angular app setup."""

    def __init__(
        self,
        cache_manager: BaseCache,
        cache_key: str,
        expire_after: int,
    ):
        """Inject dependencies."""
        self._cache_key = cache_key
        self._expire_after = expire_after
        self._cache = cache_manager

    def get_config(self):
        """:returns config content."""
        config_file_content = self._cache.get(self._cache_key)
        if not config_file_content:
            config_file_content = "backend = {0}".format(
                json.dumps({"config": self._get_config_map()}),
            )
        self._cache.add(
            self._cache_key,
            config_file_content,
            timeout=self._expire_after,
        )
        return config_file_content

    def _get_config_map(self) -> Dict[str, str]:
        return {
            "firstWeekDay": config.FIRST_WEEK_DAY,
            "currencyCode": config.CURRENCY_CODE,
            "gitlabLoginEnabled": config.GITLAB_LOGIN_ENABLED,
            "demoMode": config.DEMO_MODE,
        }


get_config = BackendConfigService(
    cache_manager=cache,
    cache_key=_CACHE_KEY,
    expire_after=_CACHE_EXPIRE_AFTER,
).get_config
