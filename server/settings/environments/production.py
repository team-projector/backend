# -*- coding: utf-8 -*-

from decouple import config

PG_PORT = 5432

SECRET_KEY = config("DJANGO_SECRET_KEY")
DOMAIN_NAME = config("DOMAIN_NAME")

ALLOWED_HOSTS = ["localhost", DOMAIN_NAME]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("DJANGO_DATABASE_HOST"),
        "PORT": config("DJANGO_DATABASE_PORT", cast=int, default=PG_PORT),
        "CONN_MAX_AGE": config("CONN_MAX_AGE", cast=int, default=60),
    },
}

STATIC_ROOT = "/var/www/static"
MEDIA_ROOT = "/var/www/media"

GITLAB_TOKEN = config("DJANGO_GITLAB_TOKEN")

SOCIAL_AUTH_GITLAB_REDIRECT_URI = "https://{0}/signup/login".format(DOMAIN_NAME)

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "DENY"
