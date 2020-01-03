# -*- coding: utf-8 -*-

SECRET_KEY = "build"  # noqa: S105

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    },
}

STATIC_ROOT = "/var/www/static"
