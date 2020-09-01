# -*- coding: utf-8 -*-

from decouple import config

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "{0}:{1}".format(
            config("DJANGO_CACHE_HOST", "memcached"),
            config("DJANGO_CACHE_PORT", "11211"),
        ),
    },
}
