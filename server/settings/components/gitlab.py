# -*- coding: utf-8 -*-

from decouple import config

GITLAB_ADDRESS = config("DJANGO_GITLAB_ADDRESS", default="https://gitlab.com")
GITLAB_NO_SYNC = config("DJANGO_GITLAB_NO_SYNC", default=False, cast=bool)
GITLAB_TOKEN = None

GITLAB_WEBHOOK_SECRET_TOKEN = config(
    "DJANGO_WEBHOOK_SECRET_TOKEN", default=None,
)

GITLAB_CHECK_WEBHOOKS = config(
    "DJANGO_GITLAB_CHECK_WEBHOOKS", default=False, cast=bool,
)
