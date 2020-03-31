# -*- coding: utf-8 -*-

SECRET_KEY = "test.key"  # noqa: S105

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postrges",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
    },
}

CELERY_TASK_ALWAYS_EAGER = True
