from typing import List

import sentry_sdk
from decouple import config
from graphql import GraphQLError
from jnt_django_toolbox.profiling.profilers.base import BaseProfiler
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from settings.components.tp import TP_APP_VERSION

LOGGING = {
    "version": 1,
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


def _before_send_sentry_handler(event, hint):
    exc_info = hint.get("exc_info")
    if exc_info:
        exc_type, exc_value, tb = exc_info
        if isinstance(exc_value, GraphQLError):
            return None

    return event


class _BeforeSendHandler:
    """Sentry before send handler."""

    def __call__(self, event, hint):
        """Filter by exception."""
        exc_info = hint.get("exc_info")
        skip_event = (
            exc_info and self._skip_by_error(exc_info)
        ) or self._skip_by_message(event)

        if not skip_event:
            return event

    def _skip_by_error(self, exc_info) -> bool:
        """Skip GraphQLError."""
        exc_type, exc_value, tb = exc_info
        return isinstance(exc_value, GraphQLError)

    def _skip_by_message(self, event) -> bool:
        """Skip read time out."""
        return "The read operation timed out" in event["logentry"]["message"]


sentry_dsn = config("DJANGO_SENTRY", default=None)
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        release=TP_APP_VERSION,
        send_default_pii=True,
        before_send=_BeforeSendHandler(),
    )
    sentry_sdk.utils.MAX_STRING_LENGTH = 4096

REQUEST_PROFILERS: List[BaseProfiler] = []
