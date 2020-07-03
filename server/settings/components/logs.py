# -*- coding: utf-8 -*-

import sentry_sdk
from decouple import config
from sentry_sdk.integrations.django import DjangoIntegration

from settings.components.tp import TP_APP_VERSION

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s]|%(levelname)s|%(module)s"  # noqa: WPS323
            + ".%(funcName)s:%(lineno)s|%(message)s",  # noqa: WPS323
            "datefmt": "%Y-%m-%d %H:%M:%S",  # noqa: WPS323
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
        release=TP_APP_VERSION,
        send_default_pii=True,
    )
    sentry_sdk.utils.MAX_STRING_LENGTH = 2048

REQUEST_PROFILERS = []
