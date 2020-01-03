# -*- coding: utf-8 -*-

from decouple import config

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("DJANGO_EMAIL_HOST", None)
EMAIL_PORT = config("DJANGO_EMAIL_PORT", None)
EMAIL_HOST_USER = config("DJANGO_EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = config("DJANGO_EMAIL_HOST_PASSWORD", None)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config("DJANGO_DEFAULT_FROM_EMAIL", None)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
