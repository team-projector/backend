# -*- coding: utf-8 -*-

from decouple import config
from jnt_django_toolbox.profiling.profilers import DatabaseQueriesProfiler

SECRET_KEY = config("DJANGO_SECRET_KEY")
DOMAIN_NAME = config("DOMAIN_NAME")

ALLOWED_HOSTS = ["localhost", DOMAIN_NAME]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DJANGO_DATABASE_NAME"),
        "USER": config("DJANGO_DATABASE_USER"),
        "PASSWORD": config("DJANGO_DATABASE_PASSWORD"),
        "HOST": config("DJANGO_DATABASE_HOST"),
        "PORT": config("DJANGO_DATABASE_PORT", cast=int, default=5432),
        "CONN_MAX_AGE": config("CONN_MAX_AGE", cast=int, default=60),
    },
}

SOCIAL_AUTH_GITLAB_REDIRECT_URI = "https://{0}/en/signup/login".format(
    DOMAIN_NAME,
)

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 31  # 31 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "DENY"

REQUEST_PROFILERS = (DatabaseQueriesProfiler(),)

FLUENTD_HOST = config("DJANGO_FLUENTD", default=None)
if FLUENTD_HOST:
    LOGGING = {
        "version": 1,
        "formatters": {
            "fluentd": {
                "()": "fluent.handler.FluentRecordFormatter",
                "exclude_attrs": ("exc_info",),
            },
        },
        "handlers": {
            "fluentd": {
                "level": "DEBUG",
                "class": "fluent.handler.FluentHandler",
                "formatter": "fluentd",
                "tag": DOMAIN_NAME,
                "host": FLUENTD_HOST,
                "port": 24224,
            },
        },
        "loggers": {
            "django": {
                "handlers": ("fluentd",),
                "level": "WARNING",
                "propagate": True,
            },
            "apps": {
                "handlers": ("fluentd",),
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }

CONSTANCE_DATABASE_CACHE_BACKEND = "default"
