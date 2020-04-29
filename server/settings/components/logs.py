# -*- coding: utf-8 -*-

import sentry_sdk
from decouple import config
from sentry_sdk.integrations.django import DjangoIntegration

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s]|%(levelname)s|%(module)s"
            + ".%(funcName)s:%(lineno)s|%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ("console",),
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ("console",),
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

sentry_dsn = config("DJANGO_SENTRY_DSN", default=None)
if sentry_dsn:
    sentry_sdk.init(  # type:ignore
        dsn=sentry_dsn,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
    )
